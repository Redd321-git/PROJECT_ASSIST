from src.llm_interface import LLMInterface
from src.rag_engine import RAGEngine
from src.schemas import InputData, IncommingData, Intent, AssistState
from sqlalchemy.orm import Session
from infra.models import User

from . import get_tools,get_dotenv,fetch_prompt_func, fetch_preferences_func
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
        self.initial_prompt=fetch_prompt_func(self.env['INITIAL_PROMPT_NAME'])
        self.aug_final_prompt=fetch_prompt_func(self.env['FINAL_STEP_PROMPT_NAME'])
        self.aug_mid_prompt=fetch_prompt_func(self.env['INTERMEDIATE_STEP_PROMPT_NAME'])
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
        
class OutputProcessor():
    def __init__(self):
        pass
    def check_if_ready_for_out():
        pass
    def process(self,state:AssistState):
        state.intent=json.loads(state.llm_output['message']['content'])
        intent=state.intent
        if intent.get('final_output') :
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
    def __init__(self,rag_engine=None,tools=None,max_steps=5):
        self.tools=tools
        self.tool_invoker=ToolInvoker(tools=self.tools)
        self.rag_engine=rag_engine if rag_engine else RAGEngine()
    async def analyze(self,state:AssistState):
        await self.rag_engine.process(state)
        self.tool_invoker.invoke(state)

class FlowManager:
    def __init__(self,llm_interface=None,rag_engine=None,tools=None):
        self.llm_interface=llm_interface if llm_interface else LLMInterface()
        self.rag_engine=rag_engine if rag_engine else RAGEngine()
        self.tools=tools
        self.in_processor=InputProcessor()
        self.intent_analyzer=IntentAnalyzer(rag_engine=self.rag_engine,tools=tools)
        self.out_processor=OutputProcessor()
    async def execute(self,state):
        self.in_processor.process(state)
        await self.llm_interface.generate_response(state)
        self.out_processor.process(state)
        await self.intent_analyzer.analyze(state)

class Assistor:
    def __init__(self,llm_interface=None,rag_engine=None,tools=None):
        self.tools=get_tools()
        self.loop=FlowManager(llm_interface=llm_interface,rag_engine=rag_engine,tools=self.tools)
        self.env=get_dotenv()
    async def assist(self, input:InputData, db: Session, user: User):
        state=AssistState(self.env['MAX_STEPS'])
        state.user_input=input
        state.user_pref=fetch_preferences_func(user.id) #fetch functions for dynamic fetching of preference 
        while not state.done:
            await self.loop.execute(state)
        return state.final_output
