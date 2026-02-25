from weaviate.classes.config import DataType
from sqlalchemy import UUID, Column, Integer, String, DateTime, ForeignKey, JSON, Text, Boolean
from infra.database import Base
import json,enum

class Roles(enum.Enum):
	admin ="admin"
	user ="user"
	assistant ="assistant"

class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID, primary_key=True, index=True, nullable=False)
    name = Column(Text, index=True)
    email = Column(Text, unique=True, index=True)
    hashed_password = Column(Text)

class UserActive(Base):
    __tablename__ = "user_active"
    user_id = Column(UUID, primary_key=True, index=True, nullable=False)
    last_active_session = Column(Text,nullable=True)
    is_active = Column(Boolean, nullable=False)
    session_id = Column(Text, nullable=True)

class UserChatActivity(Base):
    __tablename__ = "user_convo_count"
    user_id = Column(UUID, ForeignKey("users.user_id"),index=True, nullable=False)
    chat_id = Column(UUID,primary_key=True, index=True, nullable=False)
    active = Column(Boolean,default=True)
    chat_counts = Column(Integer,default=0)
    convo_count = Column(Integer,default=0)
    created_at = Column(DateTime, nullable=False)
    last_accessed = Column(DateTime, nullable=False)

class Prompts(Base):
    __tablename__ = "prompts"
    prompt_id = Column(UUID, primary_key=True, index=True)
    prompt_name = Column(Text, unique=True,index=True)
    prompt_text = Column(Text, index=True)
    description = Column(Text)
    
class UserPreferences(Base):
    __tablename__ = "user_profile"
    id = Column(UUID,primary_key=True,index=True)
    user_id = Column(UUID,ForeignKey("users.user_id"),nullable=False)
    preference_name = Column(Text,nullable=False)
    preference_mode = Column(Text,nullable=False)
    updated_at = Column(DateTime,nullable=False)
    created_at = Column(DateTime,nullable=False)

class UserPreferenceBlog(Base):
    __tablename__ = "user_preference_blog" 
    user_id = Column(UUID,ForeignKey("users.user_id"),primary_key=True,nullable=False)
    preference_blog = Column(JSON)
    last_synced = Column(DateTime,nullable=True)
    
class UserChat(Base):
    """treats one user input and one assistant response as one chat entry, stores them in a single row for easy retrieval and summary"""
    __tablename__ = "chats"
    user_id = Column(UUID,ForeignKey("users.user_id"),nullable=False)
    chat_id = Column(UUID,primary_key=True,nullable=False)
    content = Column(Text)
    timestamp = Column(DateTime,nullable=False)

class ChatSummaries(Base):
    __tablename__ = "chat_summaries"
    user_id = Column(UUID,ForeignKey("users.user_id"),nullable=False)
    chat_id = Column(UUID,ForeignKey("chats.chat_id"),primary_key=True,nullable=False)
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