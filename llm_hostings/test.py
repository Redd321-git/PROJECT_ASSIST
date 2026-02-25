import httpx
import asyncio

async def test_reasoning_api():
    async with httpx.AsyncClient(timeout=httpx.Timeout(300.0)) as client:
        message=[
            {"role":"system","content":"You are a helpful assistant that provides reasons for the given question."},
            {"role":"user","content":"Why is the sky blue?"}
        ]
        responce=await client.post("http://localhost:8001/generate_reason",json=message)
        print(responce.json())

if __name__=="__main__":
    asyncio.run(test_reasoning_api())