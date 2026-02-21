from weaviate.classes.config import DataType
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from infra.database import Base
from typing import Text
import json,enum

class Roles(enum.Enum):
	admin ="admin"
	user ="user"
	assistant ="assistant"

class User(Base):
    __tablename__ = "users"
    user_id = Column(Text, primary_key=True, index=True, nullable=False)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class UserActive(Base):
    __tablename__ = "user_active"
    user_id = Column(Text, primary_key=True, index=True, nullable=False)
    last_active_session = Column(Text,nullable=True)
    is_active = Column(bool, nullable=False)
    session_id = Column(Text, nullable=True)

class Prompts(Base):
    __tablename__ = "prompts"
    id = Column(Text, primary_key=True, index=True)
    prompt_name = Column(String, index=True)
    prompt_text = Column(String, index=True)
    description = Column(String)
    
class UserPreferences(Base):
    __tablename__ = "user_profile"
    id = Column(Text,primary_key=True,index=True)
    user_id = Column(Text,ForeignKey("users.id"),nullable=False)
    preference_name = Column(String,nullable=False)
    preference_mode = Column(String,nullable=False)
    updated_at = Column(DateTime,nullable=False)
    created_at = Column(DateTime,nullable=False)

class UserPreferenceBlog(Base):
    __tablename__ = "user_preference_blog" 
    user_id = Column(Text,ForeignKey("users.id"),primary_key=True,nullable=False)
    preference_blog = Column(JSON)
    last_synced = Column(DateTime,nullable=True)
    
class UserChat(Base):
    __tablename__ = "chats"
    user_id = Column(Text,ForeignKey("users.id"),nullable=False)
    chat_id = Column(Text,primary_key=True,nullable=False)
    content = Column(Text)
    role = Column(enum(Roles),nullable=False)
    timestamp = Column(DateTime,nullable=False)

class ChatSummaries(Base):
    __tablename__ = "chat_summaries"
    user_id = Column(Text,ForeignKey("users.id"),nullable=False)
    chat_id = Column(Text,ForeignKey("chats.chat_id"),primary_key=True,nullable=False)
    content = Column(Text)
    timestamp = Column(DateTime,nullable=False)

class userProfileClass:
    class_name="UserProfile"
    properties=[
        {"name":"user_id","dataType":DataType.TEXT},
        {"name":"preferences","dataType":DataType.TEXT},
        {"name":"style","dataType":DataType.TEXT},
        {"name":"goals","dataType":DataType.TEXT},
        {"name":"timestamp","dataType":DataType.DATE}
    ]
    description="contains users prifiles their ids, prefernces, style and goals"

class documentClass:
    class_name="Documents"
    properties=[
        {"name":"user_id","dataType":DataType.TEXT},
        {"name":"title","dataType":DataType.TEXT},
        {"name":"doc_id","dataType":DataType.TEXT},
        {"name":"content","dataType":DataType.TEXT},
        {"name":"timestamp","dataType":DataType.DATE}
    ]
    descripiton=""

class EpisodicMemoryClass:
    class_name="EpisodicMemory"
    properties=[
        {"name":"doc_id","dataType":DataType.TEXT},
        {"name":"user_id","dataType":DataType.TEXT},
        {"name":"session_id","dataType":DataType.TEXT},
        {"name":"event_type","dataType":DataType.TEXT},
        {"name":"content","dataType":DataType.TEXT},
        {"name":"timestamp","dataType":DataType.DATE}
    ]
    description=""

class SemanticMemroyClass:
    class_name="SemanticMemroy"
    properties=[
        {"name":"doc_id","dataType":DataType.TEXT},
        {"name":"user_id","dataType":DataType.TEXT},
        {"name":"content_type", "dataType":DataType.TEXT},
        {"name":"content", "dataType":DataType.TEXT},
        {"name":"tags", "dataType":DataType.TEXT},
        {"name":"timestamp","dataType":DataType.DATE}
    ]
    description=""

class TaskClass:
    class_name="Task"
    properties=[
        {"name":"user_id","dataType":DataType.TEXT},
        {"name":"task_id","dataType":DataType.TEXT},
        {"name":"description","dataType":DataType.TEXT},
        {"name":"status","dataType":DataType.TEXT},
        {"name":"timestamp","dataType":DataType.DATE}
    ]
    description=""

'''class chatClass:
    class_name="Chat"
    properties=[
        {"name":"user_id","dataType":DataType.TEXT},
        {"name":"chat_id","dataType":DataType.TEXT},
        {"name":"message","dataType":DataType.TEXT},
        {"name":"timestamp","dataType":DataType.DATE}
    ]
    description=""'''

'''class WorkingMemoryClass:
    class_name="WorkingMemory"
    properties=[
        {"name":"user_id","dataType":DataType.TEXT},
        {"name":"session_id", "dataType": DataType.TEXT},
        {"name":"context", "dataType": DataType.TEXT},
        {"name":"expires_at", "dataType": DataType.DATE},
    ]
    description=""'''