from weaviate import WeaviateClient
from infra.models import User, UserActive
from src.schemas import AssistState, SessionData
import json

class PropertyConstructor:
    def __init__(self, assist_memory_schema:dict):
        self.assist_memory_schema=assist_memory_schema
    def construct(
            self,
            memory_type:str, 
            data:dict, 
            user_data:User, 
            session_data:SessionData
            ):
        property={}
        cls=self.assist_memory_schema.get(memory_type)
        if cls is None:
            return
        for x in cls['properties']:
            attr=x['name']
            if data.get(attr):
                property[attr]=data[attr]
            elif getattr(user_data,attr):
                property[attr]=getattr(user_data,attr)
            elif getattr(session_data,attr):
                property[attr]=getattr(session_data,attr)
            else :
                property[attr]=None
        mem_obj={
            'memory_type':memory_type,
            'content':property
        }
        return mem_obj

class Retriever:
    def __init__(self, weaviate_client_: WeaviateClient):
        self.weaviate_client=weaviate_client_
    def retrieve(self, opr:dict,user_data:User):
        if opr.get('memory_type'):
            memory=self.weaviate_client.collections.use(opr['memory_type'])
            response=memory.query.hybrid(
                limit=3,
                query=opr.get('rag_query')
            )
            res=[f"MEMORY::{opr['memory_type'].upper()}"]
            for o in response.objects:
                for attr in opr["attrs"]:
                    r=o.properties.get(attr)
                    if r is not None:
                        res.append(f"{attr} : {r}")
            if len(res)==1 : 
                return None
            return '\n'.join(res)
        
class Memorizer:
    def __init__(self, weaviate_client: WeaviateClient, batch_size: int):
        self.weaviate_client=weaviate_client
        self.batch_size=batch_size
    def store_single(self, mem_obj:dict):
        try:
            if mem_obj.get('memory_type') and mem_obj.get('content'):
                memory=self.weaviate_client.collections.use(mem_obj['memory_type'])
                memory.data.insert(mem_obj['content'])
        except Exception as e:
            print(f"error detected {e}")
    def store_batch(self, memory_buffer:list[dict], memory_type:str):
        try:
            memory=self.weaviate_client.collections.use(memory_type)
            with memory.batch.fixed_size(batch_size=self.batch_size) as batch:
                for mem_obj in memory_buffer:
                    if mem_obj.get('content') : batch.add_object(properties=mem_obj['content'])
            if len(memory.batch.failed_objects)>=1:
                return {'data_insertion':'failure'}
            return {'data_insertion':'success'}
        except Exception as e:
            print(f"error detected {e}")

class MemoryController:
    def __init__(
            self,
            memorizer:Memorizer,
            assist_memory:dict,
            assist_memory_schema:dict
            ):
        self.memorizer=memorizer
        self.assist_memory=assist_memory
        self.assist_memory_schema=assist_memory_schema
        self.memory_buffers={
            memory_type:[] for memory_type in self.assist_memory
        }
        self.buffer_limits={memory_type:self.assist_memory_schema[memory_type]['buffer_limit'] for memory_type in self.assist_memory}
        self.property_constructor=PropertyConstructor(assist_memory_schema=self.assist_memory_schema)
    def _add_to_memory(self,mem_type,mem_obj:dict,user_data:User,session_data:SessionData):
        if self.assist_memory.get(mem_type):
                mem_obj=self.property_constructor.construct(memory_type=mem_type,data=mem_obj,user_data=user_data,session_data=session_data)
                self.memory_buffers[mem_type].append(mem_obj)
                if len(self.memory_buffers[mem_type])>self.buffer_limits[mem_type]:
                    self.memorizer.store_batch(self.memory_buffers[mem_type],mem_type)
                    self.memory_buffers[mem_type].clear()
    def verify(self,suggestion: list,user_data:User,session_data:SessionData):
        #i thought of adding some determisitic rules for llm direclty adding data to memory so i can limit control of llm over memory
        #but as of now i direclty let them use memory to remember 
        for obj in suggestion:
            mem_type=obj.get("memory_type")
            self._add_to_memory(mem_type=mem_type,mem_obj=obj,user_data=user_data,session_data=session_data)
    def consolidate(self,user_data:User,session_data:SessionData,consol_window:dict):
        for mem_type,obj in consol_window.items():
            self._add_to_memory(mem_type=mem_type,mem_obj=obj,user_data=user_data,session_data=session_data)

class RAGEngine:
    def __init__(
            self,
            memory_controller: MemoryController,
            weaviate_client : WeaviateClient
            ):
        self.weaviate_client=weaviate_client
        self.retriever=Retriever(self.weaviate_client)
        self.memory_controller=memory_controller
    def process(self, state:AssistState,user:User):
        req=state.reqs.get('rag_req',{})
        relevent_content=[]
        suggested_memorize_data=[]
        for sno,opr in req.items():
            if opr['task_type']=="retrieve" :
                res=self.retriever.retrieve(opr)
                if res is not None:
                    relevent_content.append(res)
            elif opr['task_type']=='memorize':
                opr['chat_id']=state.chat_id
                suggested_memorize_data.append(opr)
            else:
                pass
                # some logic to let the admin know of the raised error
        state.relevent_content= '\n'.join(relevent_content) if len(relevent_content)>=1 else None
        self.memory_controller.verify(suggested_memorize_data,user_data=user,session_data=state.session_data)
    def consolidate(self,user:User,session_data:UserActive,session_snapshot):
        consol_window=json.loads(session_snapshot)
        self.memory_controller.consolidate(user_data=user,session_data=session_data,consol_window=consol_window)

