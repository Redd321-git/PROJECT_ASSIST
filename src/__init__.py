import os
import importlib
from pathlib import Path
from dotenv import dotenv_values

tools_dir=Path(__file__).parent / "tools"
dotenv_path=Path(__file__).parent.parent / ".env"
def get_tools():
    tools = {}
    for file in tools_dir.glob("*.py"):
        if file.name != "__init__.py":
            module_name = file.stem
            module = importlib.import_module(f"src.tools.{module_name}")
            cls=getattr(module, module_name.capitalize())
            tools[module_name]=cls()
    return tools

def get_dotenv():
    return dotenv_values(dotenv_path)
    
from infra import get_assist_memory_schema,get_assist_memory_types

assist_memory=get_assist_memory_types()
assist_memory_schema=get_assist_memory_schema()
