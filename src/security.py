from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime,timedelta,timezone
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette.status import WS_1008_POLICY_VIOLATION
from infra.models import User, UserActive
from infra.database import get_db
from src import get_dotenv
import uuid

env_file=get_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")
credentials_exception = HTTPException(
	status_code=status.HTTP_401_UNAUTHORIZED,
	detail="Could not validate credentials",
	headers={"WWW-Authenticate": "Bearer"},
)

def generate_session_id():
	return uuid.uuid4()

def generate_unique_id():
	return uuid.uuid4()

def generate_doc_id():
	return uuid.uuid4()

def generate_task_id():
	return uuid.uuid4()

def generate_chat_id():
	return uuid.uuid4()

def generate_timestamp():
	return datetime.now(timezone.utc)

def get_password_hash(password :str):
	return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
	return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data: dict, expires_delta: timedelta =None):
	to_encode =data.copy()
	if expires_delta:
		expire = generate_timestamp() + expires_delta
	else:
		expire = generate_timestamp() + timedelta(minutes=int(env_file['ACCESS_TOKEN_EXPIRE_MINUTES']))
	to_encode.update({"exp": expire})
	encoded_jwt=jwt.encode(to_encode,env_file['SECRET_KEY'],algorithm=env_file['ALGORITHM'])
	return encoded_jwt

def get_current_user(
		token:str=Depends(oauth2_scheme),
		db:Session=Depends(get_db)
		)->User :
	from src.crud import get_user_by_email
	print("DEBUG: Inside get_current_user")
	print(f"DEBUG: Received token: {token}")
	try:
		payload=jwt.decode(token,env_file['SECRET_KEY'],algorithms=[env_file['ALGORITHM']])
		print(f"DEBUG: Decoded JWT payload: {payload}")
		email: str =payload.get("sub")
		if email is None:
			print("DEBUG: Email not found in token payload")
			raise credentials_exception
		user = get_user_by_email(db,email)
		if user is None:
			print("DEBUG: User not found in database")
			raise credentials_exception
		print(f"DEBUG: Authenticated user: {user.email}")
		return user
	except JWTError as e:
		if "Signature has expired" in str(e):
			raise HTTPException(status_code=401, detail="Token has expired. Please log in again.")
		raise credentials_exception
		
def get_session_data(
		db:Session=Depends(get_db),
		current_user:User=Depends(get_current_user)
		)->UserActive:
	from src.crud import get_user_active
	session_data = get_user_active(db, user_id=current_user.user_id)
	return session_data

def websocket_get_current_user(websocket: WebSocket,token: str):
	from src.crud import get_user_by_email
	if not token:
		return websocket.close(code=WS_1008_POLICY_VIOLATION)
	try:
		payload=jwt.decode(token,env_file['SECRET_KEY'],algorithms=[env_file['ALGORITHM']])
		print(f"DEBUG: Decoded JWT payload: {payload}")
		email: str =payload.get("sub")
		if email is None:
			print("DEBUG: Email not found in token payload")
			raise ValueError("invalid token")
		db_gen = get_db()
		db: Session = next(db_gen)
		user = get_user_by_email(db,email)
		db.close()
		if user is None:
			print("DEBUG: User not found in database")
			raise ValueError("user not found")
		print(f"DEBUG: Authenticated user: {user.email}")
		return user
	except (JWTError, ValueError) as e:
		return websocket.close(code=WS_1008_POLICY_VIOLATION)	
