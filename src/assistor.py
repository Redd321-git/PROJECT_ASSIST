from src.schemas import InputData, IncommingData, Intent, AssistState
from sqlalchemy.orm import Session
from infra.models import User, UserActive
from src.rag_engine import RAGEngine
from src.llm_interface import LLMInterface
from src import get_tools,get_dotenv
from src.crud import fetch_preferences, fetch_chat_summary, update_chat_summary, get_convo_count, update_convo_count, increment_convo_count,store_chat
from typing import Text
import json,re
from src.security import generate_chat_id

class ToolInvoker:
    def __init__(self,tools):
        self.tools=tools
    def invoke(self,state:AssistState):
        lines=[]
        tools_req=state.reqs.get('tools_req',{})
        for tool_name,tool_params in tools_req.items():
            lines.append(f"\n{tool_name.upper()} RESULT :")
            lines.append(self.tools[tool_name].execute(tool_params))
        state.tool_responses="\n".join(lines)
        
class InputProcessor:
    def __init__(self,prompts:dict):
        self.env=get_dotenv()
        self.initial_prompt=prompts.get(self.env['INITIAL_PROMPT_NAME'])
        self.aug_final_prompt=prompts.get(self.env['FINAL_STEP_PROMPT_NAME'])
        self.aug_mid_prompt=prompts.get(self.env['INTERMEDIATE_STEP_PROMPT_NAME'])
        self.summarizer_prompt=prompts.get(self.env['CHAT_SUMMARIZE_PROMPT_NAME'])
    def process(self,state:AssistState):
        msg=[]
        msg.append({
            "role":"system",
            "content":self.initial_prompt
            })
        if state.user_pref is not None:
            msg.append({
                "role":"system",
                "content":state.user_pref
                })
        if state.current_step>=state.max_steps:
            msg.append({
                "role":"system",
                "content":self.aug_final_prompt
            })
        elif state.current_step>0:
            msg.append({
                "role":"system",
                "content":self.aug_mid_prompt
            })
        if state.relevent_content is not None:
            msg.append({
                "role":"system",
                "content":state.relevent_content
            })
        if state.tool_responses is not None:
            msg.append({
                "role":"tool",
                "content":state.tool_responses
            })
        msg.append({
            "role":"user",
            "content":state.user_input
        })
        state.llm_input=msg
    def build_consolidation_message(self,state:AssistState):
        msg=[]
        msg.append({
            'role':'system',
            'content':self.summarizer_prompt
        })
        chat=""
        console_window=state.consol_window
        for m in console_window:
            chat+=f"{m['role'].title()}: {m['content']}\n"
        msg.append({
            'role':'user',
            'content':f'summarize the following chat=[{chat}]'
        })
        return msg

class OutputProcessor():
    def __init__(self):
        pass
    def check_if_ready_for_out():
        pass
    def process(self,state:AssistState):
        raw_content=state.llm_output['message']['content']
        match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if not match:
            raise ValueError(f"Invalid LLM JSON output: {raw_content}")
        json_str = match.group(0)
        state.intent = json.loads(json_str)
        intent=state.intent
        if intent.get('final_output'):
            state.final_output=intent['final_output']
            state.done=True
            return
        if intent.get("required_tools"):
            state.reqs["tools_req"]=intent["required_tools"]
        if intent.get("memory_oprs"):
            state.reqs["rag_req"]=intent["memory_oprs"]
        state.current_step+=1
        if state.current_step>state.max_steps:
            state.done=True
            state.final_output="error in generating response"

class IntentAnalyzer:
    def __init__(self,rag_engine:RAGEngine,tools=None,max_steps=5):
        self.tools=tools
        self.tool_invoker=ToolInvoker(tools=self.tools)
        self.rag_engine=rag_engine 
    def analyze(self,state:AssistState,user:User):
        self.rag_engine.process(state,user=user)
        self.tool_invoker.invoke(state)

class StateRepo:
    def __init__(self):
        pass
    def fetch_chat_summary(self,db:Session,state:AssistState,user:User):
        summary=fetch_chat_summary(db=db,user_id=user.user_id,chat_id=state.chat_id)
        return summary if summary else None
    def get_convo_count(self,db:Session,state:AssistState,user:User):
        return get_convo_count(db=db,user_id=user.user_id,chat_id=state.chat_id)
    def update_convo_count(self,db:Session,state:AssistState,user:User):
        update_convo_count(db=db,user_id=user.user_id,chat_id=state.chat_id,count=state.convo_count)
    def increment_convo_count(self,db:Session,state:AssistState,user:User):
        return increment_convo_count(db=db,user_id=user.user_id,chat_id=state.chat_id)
    def save_chat(self,db:Session,state:AssistState,user:User):
        store_chat(db=db,user_id=user.user_id,chat_id=state.chat_id,user_input=state.user_input,assistant_output=state.final_output)
    def fetch_user_preferences(self,db:Session,user:User):
        pref=fetch_preferences(db=db,current_user=user)
        return pref
    def update_chat_summary(self,db:Session,state:AssistState,user:User,summary:Text):
        update_chat_summary(db=db,user_id=user.user_id,chat_id=state.chat_id,summary=summary)

class MemoryConsolidator:
    def __init__(self,in_processor:InputProcessor,state_repo:StateRepo,llm_interface:LLMInterface,rag_engine:RAGEngine):
        self.llm_interface=llm_interface
        self.rag_engine=rag_engine
        self.state_repo=state_repo
        self.in_processor=in_processor
    async def consolidate_memory(self,db:Session,user:User,state:AssistState):
        msg=self.in_processor.build_consolidation_message(state=state)
        responce = await self.llm_interface.summarize(msg)
        self.state_repo.update_chat_summary(db=db,user=user,state=state,summary=responce['message']['content'])
        self.rag_engine.consolidate(user=user,session_data=state.session_data,session_snapshot=responce['message']['content'])
        state.consol_window.clear()
        state.convo_count=0

class FlowManager:
    def __init__(self,in_processor:InputProcessor,llm_interface:LLMInterface,rag_engine:RAGEngine,tools=None):
        self.llm_interface=llm_interface 
        self.rag_engine=rag_engine 
        self.tools=tools
        self.in_processor=in_processor
        self.intent_analyzer=IntentAnalyzer(rag_engine=self.rag_engine,tools=tools)
        self.out_processor=OutputProcessor()
    async def execute(self,state:AssistState,user:User):
        self.in_processor.process(state)
        await self.llm_interface.generate_response(state)
        self.out_processor.process(state)
        self.intent_analyzer.analyze(state=state,user=user)

class StateManager:
    def __init__(self,max_steps:int,consolidation_bound:int,state_repo:StateRepo,memory_consolidator:MemoryConsolidator,loop_manager:FlowManager):
        self.max_steps=max_steps
        self.max_bound=consolidation_bound
        self.loop_manager=loop_manager
        self.memmory_consolidator=memory_consolidator
        self.state_repo=state_repo
    def get_state(self,db:Session,user:User,chat_id: Text,session_data:UserActive)->AssistState:
        pref=self.state_repo.fetch_user_preferences(db=db,user=user)
        if pref is None:
            pref_blog={}
        else:
            pref_blog=getattr(pref,"preference_blog",{})
        blog=[f"{attr} : {txt}" for attr,txt in pref_blog.items()]
        if chat_id is None:
            chat_id=generate_chat_id()
            state=AssistState(chat_id=chat_id,max_steps=self.max_steps)
            state.user_pref="\n".join(blog)
        else:
            state=AssistState(chat_id=chat_id,max_steps=self.max_steps)
            state.user_pref="\n".join(blog)
            state.convo_count=self.state_repo.get_convo_count(db=db,state=state,user=user)
            state.prev_chat_summary=self.state_repo.fetch_chat_summary(db=db,state=state,user=user)
        state.session_data=session_data
        return state
    async def update_state(self,db:Session,state:AssistState,user:User,chat_id: Text):
        state.consol_window.append({
            'role':'user',
            'content':state.user_input
            })
        state.consol_window.append({
            'role':'assistant',
            'content':state.final_output
            })
        self.state_repo.save_chat(db=db,user=user,state=state)
        state.convo_count=self.state_repo.increment_convo_count(db=db,state=state,user=user)
        if state.convo_count>self.max_bound : 
            await self.memmory_consolidator.consolidate_memory(db=db,user=user,state=state)
            self.state_repo.update_convo_count(db=db,state=state,user=user)
            state.prev_chat_summary=self.state_repo.fetch_chat_summary(db=db,state=state,user=user)
        return

class Assistor:
    def __init__(self,flow_manager:FlowManager,state_manager:StateManager):
        self.tools=get_tools()
        self.env=get_dotenv()
        self.loop=flow_manager
        self.state_manager=state_manager
    async def assist(self, db:Session,input:InputData, user: User,Session_Data:UserActive, chat_id: Text):
        state=self.state_manager.get_state(db=db,user=user,chat_id=chat_id,session_data=Session_Data)
        state.user_input=input.content
        while not state.done:
            await self.loop.execute(state=state,user=user)
        await self.state_manager.update_state(db=db,state=state,user=user,chat_id=chat_id)
        return state.final_output