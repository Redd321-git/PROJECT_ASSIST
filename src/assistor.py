from src.schemas import InputData, IncommingData, Intent, AssistState
from sqlalchemy.orm import Session
from infra.models import User
from src.rag_engine import RAGEngine
from src.llm_interface import LLMInterface
from src import get_tools,get_dotenv
from src.crud import fetch_prompt, fetch_preferences, fetch_chat_summary
from typing import Text
import json

class ToolInvoker:
    def __init__(self,tools):
        self.tools=tools
    def invoke(self,state:AssistState):
        lines=[]
        for tool_name,tool_params in state.reqs['tools_req'].items():
            lines.append(f"\n{tool_name.upper()} RESULT :")
            lines.append(self.tools[tool_name].execute(tool_params))
        state.tool_responses="\n".join(lines)
        
class InputProcessor:
    def __init__(self):
        self.env=get_dotenv()
        self.initial_prompt=fetch_prompt(self.env['INITIAL_PROMPT_NAME'])
        self.aug_final_prompt=fetch_prompt(self.env['FINAL_STEP_PROMPT_NAME'])
        self.aug_mid_prompt=fetch_prompt(self.env['INTERMEDIATE_STEP_PROMPT_NAME'])
    def process(self,state:AssistState):
        msg=[]
        msg.append({
            "role":"system",
            "content":self.initial_prompt
            })
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
    def build_consolidation_message(self,consol_window):
        summarizer_prompt=fetch_prompt(self.env['CHAT_SUMMARIZE_PROMPT_NAME'])
        msg=[]
        msg.append({
            'role':'system',
            'content':summarizer_prompt
        })
        for m in consol_window:
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
        state.intent=json.loads(state.llm_output['message']['content'])
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
    async def analyze(self,state:AssistState):
        await self.rag_engine.process(state)
        self.tool_invoker.invoke(state)

class FlowManager:
    def __init__(self,llm_interface:LLMInterface,rag_engine:RAGEngine,tools=None):
        self.llm_interface=llm_interface 
        self.rag_engine=rag_engine 
        self.tools=tools
        self.in_processor=InputProcessor()
        self.intent_analyzer=IntentAnalyzer(rag_engine=self.rag_engine,tools=tools)
        self.out_processor=OutputProcessor()
    async def execute(self,state):
        self.in_processor.process(state)
        await self.llm_interface.generate_response(state)
        self.out_processor.process(state)
        await self.intent_analyzer.analyze(state)
    async def consolidate_memory(self,consol_window):
        msg=self.in_processor.build_consolidation_message(consol_window)
        responce = await self.llm_interface.summarize(msg)
        self.rag_engine.consolidate(responce['message']['content'])

class Assistor:
    def __init__(self,consolidation_bound=5,llm_interface:LLMInterface=None,rag_engine:RAGEngine=None,tools=None):
        self.tools=get_tools()
        self.loop=FlowManager(llm_interface=llm_interface,rag_engine=rag_engine,tools=self.tools)
        self.env=get_dotenv()
        self.convo_count=0
        self.max_bound=consolidation_bound
        self.consol_window=[]
        #self.previous_inference=None
    async def assist(self, input:InputData, db: Session, user: User, chat_id: Text):
        self.convo_count=self.convo_count+1
        state=AssistState(self.env['MAX_STEPS'])
        state.user_input=input
        state.chat_id=chat_id
        state.prev_chat_summary=fetch_chat_summary(db=db,chat_id=chat_id,user_id=user.id)
        pref=fetch_preferences(db,user.id)
        blog=[f"{attr} : {txt}" for attr,txt in getattr(o=pref,name="preference_blog").items()]
        state.user_pref="\n".join(blog)
        while not state.done:
            await self.loop.execute(state)
        self.consol_window.append({
            'role':'user',
            'content':state.user_input
            })
        self.consol_window.append({
            'role':'assistant',
            'content':state.final_output
            })
        if self.convo_count>self.max_bound : 
            self.loop.consolidate_memory(self.consol_window)
            self.consol_window.clear()
            self.convo_count=0
            pass
        return state.final_output