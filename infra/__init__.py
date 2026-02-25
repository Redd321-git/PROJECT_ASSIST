from pathlib import Path
import yaml
from dotenv import dotenv_values

def load_db_config():  
    with open(Path(__file__).parent/"db_config.yaml", 'r') as f:
        db_config = yaml.safe_load(f)
    return db_config

db_config_=load_db_config()

def get_assist_memory_types(db_config=db_config_):
    return db_config['weaviate_classes'] 
def get_assist_memory_schema(db_config=db_config_):
    return db_config['classes']
dotenv_path=Path(__file__).parent.parent/".env"

def get_dotenv():
    return dotenv_values(dotenv_path)

def create_weaviate_client():
    from infra.database import create_weaviate_client
    return create_weaviate_client