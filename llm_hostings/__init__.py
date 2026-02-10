import ollama
import subprocess
import time
import asyncio
import requests 
from fastapi import HTTPException

def install_ollama():
	try:
		subprocess.run(["ollama","--version"],check=True)
		print("ollama already installed")
	except FileNotFoundError:
		print("Install ollama")
		
	except subprocess.CalledProcessError:
		print("ollama not found")

loaded_models={
	"reason":None,
	"logic":None,
	"embedding":None
}
locks={
	"logic":asyncio.Lock(),
	"reason":asyncio.Lock(),
	"embedding":asyncio.Lock()
}
last_access={
	"reason":None,
	"logic":None,
	"embedding":None
}
	
default_models={
	"reason":"qwen2.5-coder:7b",					
	"logic":"qwen2.5-coder:7b",
	"embedding": "bge-m3"
}

UNLOAD_TIMEOUT=5						# need to descide timeout value in seconds
async def load_model(task_type:str,model_name:str):
	print("acquring lock")
	async with locks[task_type]:
		if loaded_models[task_type] is None:
			try:
				print("sending suprocess request")
				result=subprocess.run(["ollama","pull",model_name],capture_output=True,text=True,check=True)
				loaded_models[task_type]=model_name		
				print(f"model loaded {model_name}")
				print(result)
				last_access[task_type]=time.time()
			except subprocess.CalledProcessError as e:
				print("load failed")
				print(e)
		
	return loaded_models[task_type]

async def load_default_models():
	try:
		for action_type,model_name in default_models.items():
			load_model(action_type,model_name)
	except Exception as e:
		raise HTTPException(status_code=500,detail=str(e))
	
async def check_if_loaded(task_type:str):
	if loaded_models[task_type]:
		return True
	return False

'''async def force_unload_model(model_name:str):
	while True:
		await asyncio.sleep()					# need to specify sleep time
		async with locks[key]:
			if loaded_models[key]:
				idle_time=time.time()-last_access(key,0)
				if idle_time>UNLOAD_TIMEOUT:
					try:
						requests.post("http://loaclhost:11434/api/stop",json={"model":model_name})
						loaded_models[key]=None
						print(f"model unloaded {model_name}")
						break
					except Exception as e:
						print(e)'''