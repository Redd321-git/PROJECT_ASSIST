import weaviate
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from infra import get_dotenv

env_file=get_dotenv()
url=f"postgresql://{env_file['DB_USER']}:{env_file['DB_PASSWORD']}@{env_file['DB_HOST']}:{env_file['DB_PORT']}/{env_file['DB_NAME']}"

engine=None
sessionlocal=None

def create_db_engine():
    global engine
    engine=create_engine(url)
    return engine

def create_session_local(engine):
    global sessionlocal
    sessionlocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
    return sessionlocal

header={
        "X-Cohere-Api-Key": env_file['COHERE_API_KEY']
    }

def create_weaviate_client(host=env_file["WEAVIATE_HOST"],port=env_file["WEAVIATE_PORT"],grpc_port=env_file["WEAVIATE_GRPC_PORT"]):
    client=weaviate.connect_to_local(headers=header,host=host,port=port,grpc_port=grpc_port)
    return client

Base=declarative_base()

def get_session_local():
    global engine, sessionlocal
    if engine is None:
        engine=create_db_engine()
        sessionlocal=create_session_local(engine)
    return sessionlocal

def get_db():
    db=sessionlocal()
    try:
        yield db
    finally:
        db.close()

    