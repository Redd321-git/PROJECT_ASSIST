from src.schemas import AssistState
from . import get_dotenv
import requests
import subprocess
import httpx

class LLMInterface:
    def __init__(self):
        self.env_file=get_dotenv()
        self.llm_url=self.env_file['LLM_REASONING_API_URL']
    async def generate_response(self, state:AssistState):
        async with httpx.AsyncClient() as client:
            responce=await client.post(self.llm_url,data=state.llm_input)
        state.llm_output=responce
    async def summarize(self,msg):
        async with httpx.AsyncClient() as client:
            responce=await client.post(self.llm_url,data=msg)
        return responce