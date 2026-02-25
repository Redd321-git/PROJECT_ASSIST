from fastapi import FastAPI,HTTPException
import ollama
from . import default_models, install_ollama, load_model, check_if_loaded # ,force_unload_model
import uvicorn, asyncio, time, subprocess


app=FastAPI()

models={
	"reason": None,					
	"logic": None,
	"embedding": None
}


@app.post("/generate_reason")
async def generate_reason(message: list[dict]):
	model=default_models["reason"] if models["reason"] is None else models["reason"]
	try:
		if not await check_if_loaded("reason"):
			await load_model("reason",model)
		responce=ollama.chat(
				model=model,
				messages=message
			)
		return responce
	except Exception as e:
		raise HTTPException(status_code=500,detail=str(e))

@app.post("/generate_logic")
async def generate_logic(message: dict):
	model=default_models["logic"] if models["logic"] is None else models["logic"]
	try:
		if not await check_if_loaded("logic"):
			await load_model("logic",model)
		responce=ollama.generate(
				model=model,
				prompt=message["input"]
			)
		return responce
	except Exception as e:
		raise HTTPException(status_code=500,detail=str(e))
	
@app.post("/genrate_embedding")
async def generate_embedding(message: dict):
	#print("checking if loaded")
	model=default_models["embedding"] if models["embedding"] is None else models["embedding"]
	try:
		if not await check_if_loaded("embedding"):
			#print("loading model")
			await load_model("embedding",model)
		#print("generating responce")
		responce=ollama.embed(
				model=model,
				input=message["text"]
			)
		#print(responce)
		return responce
	except Exception as e:
		raise HTTPException(status_code=500,detail=str(e))
	
@app.post("/change_default_models")
async def change_default_models(model_name:str, action_type:str):
	if default_models[action_type]==model_name:
		return {"message":"no change made, already using the specified model"}
	load_model(model_name)
	models[action_type]=model_name
	return {"message":f"default model for {action_type} changed to {model_name}"}

if __name__=="__main__":
	import uvicorn
	uvicorn.run("llm_hostings.main:app",host="0.0.0.0",port=8001, reload=True, workers=1)
	install_ollama()