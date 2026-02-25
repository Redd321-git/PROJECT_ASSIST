from sqlalchemy.orm import Session
from infra.models import Prompts, User, UserChat, UserChatActivity, UserPreferenceBlog, ChatSummaries, UserActive
from fastapi import Depends,HTTPException
from src.schemas import UserCreate
from src.security import get_password_hash,generate_unique_id,generate_chat_id,generate_timestamp
from typing import Text

def fetch_prompt(db:Session,prompt_name:Text):
	prompt=db.query(Prompts).filter(Prompts.prompt_name==prompt_name).first()
	return prompt.prompt_text if prompt else None

def fetch_preferences(db:Session,current_user: User):
    responce=db.query(UserPreferenceBlog).filter(UserPreferenceBlog.user_id==current_user.user_id).first()
    return responce

def create_user(db: Session, user: UserCreate):
	existing_user=db.query(User).filter((User.name == user.username )).first()
	if existing_user:
		raise HTTPException(status_code=400,detail="username already exists")
	hashed_password=get_password_hash(user.password)
	db_user=User(
		name=user.username,
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

def get_user_active(db:Session,user_id: Text):
	activity =db.query(UserActive).filter(UserActive.user_id == user_id).first()
	return activity

def update_last_active(db: Session, user_id: Text, lst_active_session):
	db.query(UserActive).filter(UserActive.user_id == user_id).update({"last_active_session": lst_active_session})
	db.commit()

def update_current_active(db:Session, user_id: Text, session_id: Text):
	user=get_user_active(db=db,user_id=user_id)
	if user:
		user.session_id=session_id
		user.is_active=True
	else:
		new_active=UserActive(
			user_id=user_id,
			session_id=session_id,
			is_active=True,
			last_active_session=None
		)
		db.add(new_active)
	db.commit()

def user_offline(db:Session,user_id:Text,session_id: Text):
	update_last_active(db=db,user_id=user_id, lst_active_session=session_id)
	db.query(UserActive).filter(UserActive.user_id == user_id).update({"is_active": False})
	db.commit()

def get_last_active(db:Session,user_id: Text):
	activity=db.query(UserActive).filter(UserActive.user_id == user_id).first()
	return activity.session_id if activity.is_active else activity.last_active_session  

def store_chat(db:Session,user_id: Text,chat_id: Text,user_input: Text,assistant_output: Text):
	user_chat = UserChat(
		user_id=user_id,
		chat_id=chat_id,
		content=f"User: {user_input}\nAssistant: {assistant_output}",
		timestamp=generate_timestamp()
	)
	db.add(user_chat)
	db.commit()

def Store_chat_summary(db:Session,user_id: Text,chat_id: Text,summary: Text):
	summary_entry=db.query(ChatSummaries).filter(ChatSummaries.user_id==user_id,ChatSummaries.chat_id==chat_id).first()
	if summary_entry:
		update_chat_summary(db=db,user_id=user_id,chat_id=chat_id,summary=summary)
	else:
		new_summary=ChatSummaries(
			user_id=user_id,
			chat_id=chat_id,
			content=summary,
			timestamp=generate_timestamp()
		)
		db.add(new_summary)
		db.commit()

def update_chat_summary(db:Session,user_id: Text,chat_id: Text,summary: Text):
	summary_entry=db.query(ChatSummaries).filter(ChatSummaries.user_id==user_id,ChatSummaries.chat_id==chat_id).first()
	if summary_entry:
		summary_entry.content=summary
		summary_entry.timestamp=generate_timestamp()
		db.commit()
	else:
		Store_chat_summary(db=db,user_id=user_id,chat_id=chat_id,summary=summary)

def fetch_chat_summary(db:Session,user_id: Text,chat_id: Text):
	summary = db.query(ChatSummaries).filter(ChatSummaries.user_id==user_id,ChatSummaries.chat_id==chat_id).first()
	return summary.content if summary else None

def get_convo_count(db:Session,user_id: Text,chat_id: Text):
	chat_meta =db.query(UserChatActivity).filter(UserChatActivity.user_id == user_id,UserChatActivity.chat_id==chat_id).first()
	if chat_meta and chat_meta.active:
		return chat_meta.convo_count
	return 0

def create_chat_activity(db:Session,user_id: Text, chat_id: Text):
	existing_activity = db.query(UserChatActivity).filter(UserChatActivity.user_id == user_id, UserChatActivity.chat_id == chat_id).first()
	if not existing_activity:
		new_activity = UserChatActivity(
			user_id=user_id,
			chat_id=chat_id,
			active=True,
			convo_count=1,
			created_at=generate_timestamp(),
			last_accessed=generate_timestamp()
		)
		db.add(new_activity)
		db.commit()

def update_convo_count(db:Session,user_id: Text, chat_id: Text,count: int):
	chat_meta =db.query(UserChatActivity).filter(UserChatActivity.user_id == user_id,UserChatActivity.chat_id==chat_id).first()
	if chat_meta:
		chat_meta.convo_count = count
		chat_meta.last_accessed=generate_timestamp()
		db.commit()
	else:
		create_chat_activity(db=db,user_id=user_id,chat_id=chat_id)

def increment_convo_count(db:Session,chat_id: Text,user_id: Text):
	chat_meta =db.query(UserChatActivity).filter(UserChatActivity.user_id == user_id,UserChatActivity.chat_id==chat_id).first()
	if chat_meta:
		chat_meta.convo_count += 1
		chat_meta.last_accessed=generate_timestamp()
		db.commit()
	return chat_meta.convo_count if chat_meta else 0

def fetch_user_active_chats(db:Session,user_id: Text):
	active_chats=db.query(UserChatActivity).filter(UserChatActivity.user_id == user_id,UserChatActivity.active==True).all()
	return [chat.chat_id for chat in active_chats]

def fetch_chat_ids(db:Session,user_id: Text,limit: int=10,offset: int=0):
	chats=db.query(UserChat).filter(UserChat.user_id == user_id).order_by(UserChat.timestamp.desc()).limit(limit).offset(offset).all()
	return [chat.chat_id for chat in chats]

def fetch_chat_content(db:Session,user_id: Text,chat_id: Text,limit: int=20,offset: int=0):
	inference=db.query(UserChat).filter(UserChat.user_id==user_id,UserChat.chat_id==chat_id).order_by(UserChat.timestamp.desc()).limit(limit).offset(offset).all()
	return [chat.content for chat in inference] if inference else None