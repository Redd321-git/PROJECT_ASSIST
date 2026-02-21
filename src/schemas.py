from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginForm(BaseModel):
	email: str
	password: str

class UserCreate(BaseModel):
	username: str
	email: EmailStr
	password: str

class UserResponse(BaseModel):
	username: str
	email: EmailStr
	role: str
	id: str

	class Config:
		from_attributes = True

class Intent(BaseModel):
    llm_frmltd_query: str
    required_tools: Optional[list] = []
    suggested_prompt: Optional[str]

class InputData(BaseModel):
    final_output: Optional[str] = None

class IncommingData(BaseModel):
    intent: Intent
    reqs: Optional[dict] = {}

class AssistState:
    def __init__(self,max_steps=5):
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
        self.chat_id=None