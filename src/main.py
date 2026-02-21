from fastapi import FastAPI, WebSocket, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src import assist_memory, assist_memory_schema
from src.assistor import Assistor
from src.llm_interface import LLMInterface
from src.rag_engine import RAGEngine, MemoryController, Memorizer
from src.schemas import UserResponse, UserCreate
from src.security import verify_password, create_access_token, get_current_user, generate_session_id
from infra import get_db,create_weaviate_client
from src.crud import create_user, get_user_by_username, get_user_by_email, get_last_active, update_last_active, update_current_active,user_offline
from sqlalchemy.orm import Session
from datetime import timedelta
from src import get_dotenv

env_file=get_dotenv()

app=FastAPI()
weaviate_client=create_weaviate_client()
memorizer=Memorizer(weaviate_client=weaviate_client,batch_size=20)
memory_controller=MemoryController(memorizer=memorizer,assist_memory=assist_memory)
rag_engine=RAGEngine(memory_controller=memory_controller,weaviate_client=weaviate_client)
llm_interface=LLMInterface()
assistant=Assistor(llm_interface=llm_interface,rag_engine=rag_engine)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    #await websocket.send_text("Hello, WebSocket!")
    await websocket.close()

@app.post("/register",response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
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
		data={"sub":user.email}, expires_delta=timedelta(minutes=env_file['ACCESS_TOKEN_EXPIRE_MINUTES'])
	)
	#logic to update latest user active session
	session_id=generate_session_id()
	update_current_active(db=db,user_id=user.user_id,session_id=session_id)
	return {"access_token": access_token, "token_type": "bearer","message":"login successfull"}

@app.get("/me",response_model=UserResponse)
async def read_me(current_user= Depends(get_current_user)):
	return current_user

@app.post("/logout")
async def logout(db: Session= Depends(get_db)):
    user=get_current_user()
    session_id=get_last_active(user_id=user.user_id)
    user_offline(db,user_id=user.user_id,session_id=session_id)
    return {"message":"logged out"}