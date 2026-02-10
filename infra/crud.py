from sqlalchemy.orm import Session
from infra.models import Prompts, User, UserPreferenceBlog
from fastapi import Depends
from infra.database import get_db

async def fetch_prompt(db:Session):
    pass

async def fetch_preference(db:Session,current_user: User):
    responce=db.query(UserPreferenceBlog).get(current_user.id)
    return responce 