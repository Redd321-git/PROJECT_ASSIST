from . import assist_memory,weaviate_client
from schemas import AssistState

class RAGEngine:
    def __init__(self):
        self.functionality={
            'retrieve':self.retrieve,
            'store':self.store,
            'retrieve_pref':self.retrieve_pref
        }
        self.weaviate_client=weaviate_client
        self.assist_memory=assist_memory
    def retrieve_pref(self, state):
        #userpref_tab=self.weaviate_client.collections.use('UserProfile')
        pref=None
    def retrieve(self, opr):
        pass
    def store(self, opr):
        pass
    def process(self, state:AssistState):
        if state.req["rag_req"] is not None:
            for sno,opr in state.req["rag_req"]:
                if opr.task_type in self.functionality:
                    return self.functionality[opr["task_type"]](opr)
        else:
            raise ValueError(f"Unsupported task type: {opr.task_type}")