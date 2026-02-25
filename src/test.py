from src import get_dotenv, get_tools, assist_memory, assist_memory_schema
from src.assistor import Assistor,StateManager,FlowManager, MemoryConsolidator, StateRepo,InputProcessor
from src.llm_interface import LLMInterface
from src.rag_engine import RAGEngine, MemoryController, Memorizer
from src.security import generate_chat_id, generate_session_id, get_session_data, verify_password, create_access_token, get_current_user
from src.schemas import InputData, UserCreate
from src.crud import create_user, fetch_chat_content, get_user_by_username, get_user_by_email, get_last_active, update_last_active, update_current_active,user_offline, fetch_user_active_chats,fetch_prompt, fetch_chat_ids, create_chat_activity
from sqlalchemy.orm import Session
from infra import create_weaviate_client
from infra.database import get_session_local
from infra.models import Prompts,UserActive
from datetime import timedelta

import json

env_file=get_dotenv()

PROMPT_NAMES = {
    "initial_prompt": "INITIAL_PROMPT",
    "final_step_prompt": "FINAL_STEP_PROMPT",
    "intermediate_step_prompt": "INTERMEDIATE_STEP_PROMPT",
    "chat_summarize_prompt": "CHAT_SUMMARIZE_PROMPT"
}

def add_dummy_prompts(db: Session):
    dummy_prompts = [
        {"prompt_name": "initial_prompt", "prompt_text": "This is the initial prompt."},
        {"prompt_name": "final_step_prompt", "prompt_text": "This is the final step prompt."},
        {"prompt_name": "intermediate_step_prompt", "prompt_text": "This is the intermediate step prompt."},
        {"prompt_name": "chat_summarize_prompt", "prompt_text": "This is the chat summarize prompt."}
    ]
    
    for prompt in dummy_prompts:
        existing_prompt = db.query(Prompts).filter(Prompts.prompt_name == prompt["prompt_name"]).first()
        if not existing_prompt:
            new_prompt = Prompts(prompt_id=generate_session_id(),prompt_name=prompt["prompt_name"], prompt_text=prompt["prompt_text"])
            db.add(new_prompt)
    
    db.commit()

async def test_start():
    sessionlocal=get_session_local()
    db=sessionlocal()
    prompts={}
    try:
        print("DB TYPE:", type(db))
        print("IS INSTANCE:", isinstance(db, type(sessionlocal())))
        #add dummy prompts
        add_dummy_prompts(db=db)
        for prompt_name in PROMPT_NAMES:
            prompt=fetch_prompt(db=db,prompt_name=prompt_name)
            prompts[prompt_name]=prompt
            print(f"Fetched prompt {prompt_name}: {prompt}")
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
        print("Starting up the application...")
        input=InputData(content="this is a test if the system is working or not respond with 'the system is working' inside a dict with key as final_output that the function json.loads() can parse")
        user=create_user(db=db,user=UserCreate(username="testuser",email="test@gmail.com",password="testpassword"))
        session_id=generate_session_id()
        update_current_active(db=db,user_id=user.user_id,session_id=session_id)
        session_data=get_session_data(db=db,user=user)
        print(await assistor.assist(db=db,input=input, user=user,Session_Data=session_data, chat_id=generate_chat_id()))
        db.query(Prompts).delete()
        db.commit()
    finally:
        db.close()
if __name__=="__main__":
    import asyncio
    asyncio.run(test_start())