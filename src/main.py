import json
from fastapi import FastAPI, WebSocket, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from infra import create_weaviate_client
from infra.models import User, UserActive
from infra.database import get_session_local,get_db
from src import assist_memory, assist_memory_schema
from src.assistor import Assistor,StateManager,FlowManager, MemoryConsolidator, StateRepo,InputProcessor
from src.llm_interface import LLMInterface
from src.rag_engine import RAGEngine, MemoryController, Memorizer
from src.schemas import InputData, UserResponse, UserCreate,AssistRequest
from src import get_tools
from src.security import generate_chat_id, verify_password, create_access_token, get_current_user, generate_session_id, get_session_data
from src.crud import create_user, fetch_chat_content, get_user_by_username, get_user_by_email, get_last_active, update_last_active, update_current_active,user_offline, fetch_user_active_chats,fetch_prompt, fetch_chat_ids, create_chat_activity
from sqlalchemy.orm import Session
from datetime import timedelta
from src import get_dotenv
from uuid import UUID

env_file=get_dotenv()

assistor=None
state_manager=None
flow_manager=None
memory_consolidator=None
rag_engine=None
llm_interface=None
state_repo=None
weaviate_client=None
memory_controller=None
memorizer=None
prompts={}

@asynccontextmanager
async def lifespan(app: FastAPI):
	global assistor, prompts, state_manager,in_processor, flow_manager, memory_consolidator, rag_engine, llm_interface, state_repo, weaviate_client, memory_controller, memorizer
	session_local=get_session_local()
	db=session_local()
	try:
		prompt_names=list(env_file['PROMPT_NAMES'])
		for prompt_name in prompt_names:
			prompts[prompt_name]=fetch_prompt(db=db,prompt_name=prompt_name)
	finally:
		db.close()
	tools=get_tools()
	weaviate_client=create_weaviate_client()
	in_processor=InputProcessor(prompts=prompts)
	memorizer=Memorizer(weaviate_client=weaviate_client,batch_size=20)
	memory_controller=MemoryController(memorizer=memorizer,assist_memory=assist_memory,assist_memory_schema=assist_memory_schema)
	rag_engine=RAGEngine(memory_controller=memory_controller,weaviate_client=weaviate_client)
	llm_interface=LLMInterface()
	state_repo=StateRepo()
	memory_consolidator=MemoryConsolidator(in_processor=in_processor,state_repo=state_repo,llm_interface=llm_interface,rag_engine=rag_engine)
	flow_manager=FlowManager(in_processor=in_processor,llm_interface=llm_interface,rag_engine=rag_engine,tools=tools)
	state_manager=StateManager(state_repo=state_repo,max_steps=int(env_file['MAX_STEPS']),consolidation_bound=int(env_file['CONSOLIDATION_BOUND']),memory_consolidator=memory_consolidator,loop_manager=flow_manager)
	assistor=Assistor(flow_manager=flow_manager,state_manager=state_manager)
	print("Startup completed successfully")
	yield
app=FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    #await websocket.send_text("Hello, WebSocket!")
    await websocket.close()

@app.post("/register",response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
	print(type(db))
	existing_user =get_user_by_email(db,user.email)
	if existing_user:
		raise HTTPException(status_code=400,detail="Email already registered")
	user=create_user(db, user)
	return user

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session= Depends(get_db)):
	user=get_user_by_username(db,form_data.username)
	if not user or not verify_password(form_data.password, user.hashed_password):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
	access_token = create_access_token(
		data={"sub":user.email}, expires_delta=timedelta(minutes=int(env_file['ACCESS_TOKEN_EXPIRE_MINUTES']))
	)
	#logic to update latest user active session
	session_id=generate_session_id()
	update_current_active(db=db,user_id=user.user_id,session_id=session_id)
	return {"access_token": access_token, "token_type": "bearer","message":"login successfull"}

@app.get("/me",response_model=UserResponse)
async def read_me(current_user= Depends(get_current_user)):
	return current_user

@app.post("/assist")
async def assist(user_input:AssistRequest, db: Session=Depends(get_db), user: User = Depends(get_current_user), session_data: UserActive = Depends(get_session_data)):
	chat_id=user_input.chat_id
	input_data=InputData(content=user_input.input)
	try:
		response=await assistor.assist(db=db,input=input_data,user=user,Session_Data=session_data,chat_id=chat_id)
		return {"response": response}
	except Exception as e:
		raise HTTPException(status_code=500,detail=str(e))

@app.post("/load_chat_ids")
async def load_chat_ids(limit: int,offset: int=0,db: Session=Depends(get_db), user: User = Depends(get_current_user)):
	chat_ids=fetch_chat_ids(db=db,user_id=user.user_id,limit=limit,offset=offset)
	return {"chat_ids": chat_ids}

@app.post("/load_chat")
async def load_chat(chat_id: UUID, limit: int=10,offset: int=0,db: Session=Depends(get_db), user: User = Depends(get_current_user)):
	chat=fetch_chat_content(db=db,user_id=user.user_id,chat_id=chat_id,limit=limit,offset=offset)
	return {"chat": chat}

@app.post("/create_new_chat")
async def create_new_chat(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	chat_id=generate_chat_id()
	create_chat_activity(db=db,user_id=user.user_id,chat_id=chat_id)
	return chat_id

@app.post("/logout")
async def logout(user:User=Depends(get_current_user),db: Session= Depends(get_db)):
	session_id=get_last_active(db=db,user_id=user.user_id)
	active_chats=fetch_user_active_chats(db=db,user_id=user.user_id)
	for chat_id in active_chats:
		state=state_manager.get_state(db=db,user=user,chat_id=chat_id)
		await memory_consolidator.consolidate_memory(user=user,state=state)
	user_offline(db=db,user_id=user.user_id,session_id=session_id)
	return {"message":"logged out"}

if __name__=="__main__":
	import uvicorn
	uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
