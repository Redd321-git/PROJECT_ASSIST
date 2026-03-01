from src.schemas import AssistState
from . import get_dotenv
import httpx

class LLMInterface:
    def __init__(self):
        self.env_file=get_dotenv()
        self.llm_url=self.env_file['LLM_REASONING_API_URL']
    async def generate_response(self, state:AssistState):
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
            message=state.llm_input
            print(type(message))
            responce=await client.post(self.llm_url,json=message)
        print(state.llm_input)
        state.llm_output=responce.json()
        '''state.llm_output={
            'message':{'content': '{\n  "final_output": "Hello Ritesh!"\n}'}
        }'''
        #print(state.llm_output)
        print(state.llm_output['message']['content'])
    async def summarize(self,msg):
        print("trying summarization")
        print(msg)
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
            responce=await client.post(self.llm_url,json=msg)
        print(responce.json())
        print("the above is the reponse")
        return responce.json()
        '''return {
            'message':{'content': '{\n  "final_output": "Hello Ritesh!"\n}'}
        }'''