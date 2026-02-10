import weaviate
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from . import get_dotenv

env_file=get_dotenv()
url=f"postgresql://{env_file['DB_USER']}:{env_file['DB_PASSWORD']}@{env_file['DB_HOST']}:{env_file['DB_PORT']}/{env_file['DB_NAME']}"

def create_db_engine():
    engine=create_engine(url)
    sessionlocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
    return engine,sessionlocal

header={
        "X-Cohere-Api-Key": env_file['COHERE_API_KEY']
    }

def create_weaviate_client(host=env_file["WEAVIATE_HOST"],port=env_file["WEAVIATE_PORT"],grpc_port=env_file["WEAVIATE_GRPC_PORT"]):
    client=weaviate.connect_to_local(headers=header,host=host,port=port,grpc_port=grpc_port)
    return client

Base=declarative_base()

def get_db():
    engine,SessionLocal=create_db_engine()
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

    