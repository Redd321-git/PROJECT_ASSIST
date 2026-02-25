
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Text
from uuid import UUID

class LoginForm(BaseModel):
	email: str
	password: str

class UserCreate(BaseModel):
	username: str
	email: EmailStr
	password: str

class SessionData(BaseModel):
    session_id: UUID


class UserResponse(BaseModel):
	name: str
	email: EmailStr
	user_id: UUID

	model_config = ConfigDict(from_attributes = True)

class Intent(BaseModel):
    llm_frmltd_query: str
    required_tools: Optional[list] = []
    suggested_prompt: Optional[str]

class InputData(BaseModel):
    content: str

class AssistRequest(BaseModel):
    chat_id: UUID
    input: str

class IncommingData(BaseModel):
    intent: Intent
    reqs: Optional[dict] = {}

class AssistState:
    def __init__(self,chat_id:Text,max_steps=5):
        self.current_step=0
        self.max_steps=max_steps
        self.user_input=None
        self.intent=None
        self.user_pref=None
        self.prev_chat_summary=None
        self.tool_responses=None
        self.relevent_content=None
        self.reqs={}
        self.llm_input=None
        self.final_output=None
        self.done=False
        self.session_data=None
        self.chat_id=chat_id
        self.consol_window=[]
        self.convo_count=0
