import os
import importlib
from pathlib import Path
from dotenv import dotenv_values
from infra.crud import fetch_prompt, fetch_preference

tools_dir=Path(__file__).parent / "tools"
dotenv_path=Path(__file__).parent.parent / ".env"
def get_tools():
    tools = {}
    for file in tools_dir.glob("*.py"):
        if file.name != "__init__.py":
            module_name = file.stem
            module = importlib.import_module(f"tools.{module_name}")
            cls=getattr(module, module_name.capitalize())
            tools[module_name]=cls()
    return tools

def get_dotenv():
    return dotenv_values(dotenv_path)
    
from infra import get_assist_memory_schema, get_wev_client
assist_memory=get_assist_memory_schema()
weaviate_client=get_wev_client()
print(weaviate_client)

fetch_prompt_func=fetch_prompt
fetch_preference_func=fetch_preference