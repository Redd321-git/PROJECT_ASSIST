import weaviate
from infra.database import create_weaviate_client
from . import load_db_config

db_config=load_db_config()

def delete_db():
    memory=db_config['classes']
    clnt=create_weaviate_client()
    try:
        existing={i for i in clnt.collections.list_all()}
        for i in memory:
            if i['class_name'] in existing:
                clnt.collections.delete(i['class_name'])
    finally:
        clnt.close()

delete_db()
    