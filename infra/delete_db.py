import weaviate
from infra.database import create_weaviate_client
from . import load_db_config

db_config=load_db_config()

def delete_vec_db():
    memory=db_config['classes']
    clnt=create_weaviate_client()
    try:
        existing={i for i in clnt.collections.list_all()}
        for i,z in memory.items():
            if i in existing:
                clnt.collections.delete(i)
    finally:
        clnt.close()

delete_vec_db()
    