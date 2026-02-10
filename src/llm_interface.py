from src.schemas import AssistState
import requests
import subprocess
from . import get_dotenv
class LLMInterface:
    def __init__(self):
        self.env_file=get_dotenv()
        self.llm_url=self.env_file['LLM_REASONING_API_URL']
    async def generate_response(self, state:AssistState):
        responce=await requests.post(self.llm_url,data=state.llm_input)
        state.llm_output=responce
        