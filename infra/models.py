from weaviate.classes.config import DataType
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from infra.database import Base
import json

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Prompts(Base):
    __tablename__ = "prompts"
    id = Column(Integer, primary_key=True, index=True)
    prompt_name = Column(String, index=True)
    prompt_text = Column(String, index=True)
    description = Column(String)
    
class UserPreferences(Base):
    __tablename__ = "userprofile"
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    preference_name = Column(String,nullable=False)
    preference_mode = Column(String,nullable=False)
    updated_at = Column(DateTime,nullable=False)
    created_at = Column(DateTime,nullable=False)

class UserPreferenceBlog(Base):
    __tablename__ = "UserPreferenceBlog" 
    user_id = Column(Integer,ForeignKey("users.id"),primary_key=True,nullable=False)
    preference_blog = Column(JSON)
    last_synced = Column(DateTime,nullable=True)
    
class userProfileClass:
    class_name="UserProfile"
    properties=[
        {"name":"user_id","dataType":DataType.TEXT},
        {"name":"preferences","dataType":DataType.TEXT},
        {"name":"style","dataType":DataType.TEXT},
        {"name":"goals","dataType":DataType.TEXT},
        {"name":"updated_at","dataType":DataType.DATE}
    ]
    description="contains users prifiles their ids, prefernces, style and goals"

class chatClass:
    class_name="Chat"
    properties=[
        {"name":"user_id","dataType":DataType.TEXT},
        {"name":"chat_id","dataType":DataType.TEXT},
        {"name":"message","dataType":DataType.TEXT},
        {"name":"timestamp","dataType":DataType.DATE}
    ]
    description=""

class documentClass:
    class_name="Documents"
    properties=[
        {"name":"title","dataType":DataType.TEXT},
        {"name":"doc_id","dataType":DataType.TEXT},
        {"name":"content","dataType":DataType.TEXT},
        {"name":"uploaded_at","dataType":DataType.DATE}
    ]
    descripiton=""

class EpisodicMemoryClass:
    class_name="EpisodicMemory"
    properties=[
        {"name":"doc_id","dataType":DataType.TEXT},
        {"name": "user_id", "dataType": DataType.TEXT},
        {"name": "session_id", "dataType": DataType.TEXT},
        {"name": "event_type", "dataType": DataType.TEXT},
        {"name": "content", "dataType": DataType.TEXT},
        {"name":"timestamp","dataType":DataType.DATE}
    ]
    description=""

class SemanticMemroyClass:
    class_name="SemanticMemroy"
    properties=[
        {"name":"doc_id","dataType":DataType.TEXT},
        {"name": "source_id", "dataType": DataType.TEXT},
        {"name": "source_type", "dataType": DataType.TEXT},
        {"name": "content", "dataType": DataType.TEXT},
        {"name": "tags", "dataType": DataType.TEXT},
        {"name":"timestamp","dataType":DataType.DATE}
    ]
    description=""

class WorkingMemoryClass:
    class_name="WorkingMemory"
    properties=[
        {"name": "session_id", "dataType": DataType.TEXT},
        {"name": "context", "dataType": DataType.TEXT},
        {"name": "expires_at", "dataType": DataType.DATE},
    ]
    description=""

class TaskClass:
    class_name="Task"
    properties=[
        {"name":"task_id","dataType":DataType.TEXT},
        {"name":"description","dataType":DataType.TEXT},
        {"name":"status","dataType":DataType.TEXT},
        {"name":"created_at","dataType":DataType.DATE}
    ]
    description=""
