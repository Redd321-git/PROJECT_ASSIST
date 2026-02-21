from sqlalchemy.orm import Session
from infra.models import Prompts, User, UserPreferenceBlog, ChatSummaries, UserActive
from fastapi import Depends,HTTPException
from src.schemas import UserCreate
from src.security import get_password_hash,generate_unique_id
from infra.database import get_db
from typing import Text

async def fetch_prompt(db:Session,prompt_name:Text):
	prompt=db.query(Prompts).filter(Prompts.prompt_name==prompt_name).first()
	return getattr(o=prompt,name="prompt_text")

async def fetch_preferences(db:Session,current_user: User):
    responce=db.query(UserPreferenceBlog).get(current_user.user_id)
    return responce

def create_user(db: Session, user: UserCreate):
	existing_user=db.query(User).filter((User.name == user.username )).first()
	if existing_user:
		raise HTTPException(status_code=400,detail="username already exists")
	hashed_password=get_password_hash(user.password)
	db_user=User(
		username=user.username,
		email=user.email,
		hashed_password=hashed_password,
		user_id=generate_unique_id()
	)

	db.add(db_user)
	db.commit()
	db.refresh(db_user)
	return db_user

def get_user_by_email(db: Session, email: str):
	return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
	return db.query(User).filter(User.name == username).first()

def update_last_active(db: Session, user_id: Text, lst_active_session):
	db.query(UserActive).filter(UserActive.user_id == user_id).update({"last_active_session": lst_active_session})
	db.commit()

def update_current_active(db:Session, user_id: Text, session_id: Text):
	db.query(UserActive).filter(UserActive.user_id == user_id).update({"session_id": session_id,"is_active": True})
	db.commit()

def user_offline(db:Session,user_id:Text,session_id: Text):
	update_last_active(user_id=user_id,session_id=session_id)
	db.query(UserActive).filter(UserActive.user_id == user_id).update({"is_active": False})
	db.commit()

def get_last_active(db:Session,user_id: Text):
	activity=db.query(UserActive).filter(UserActive.user_id == user_id).first()
	return activity.session_id if activity.is_active else activity.last_active_session  

def get_user_active(db:Session,user_id: Text):
	activity =db.query(UserActive).filter(UserActive.user_id == user_id).first()
	return activity

def fetch_chat_summary(db:Session,user_id: Text,chat_id: Text):
	summary = db.query(ChatSummaries).filter(ChatSummaries.user_id==user_id and ChatSummaries.chat_id==chat_id).first()
	return summary.content