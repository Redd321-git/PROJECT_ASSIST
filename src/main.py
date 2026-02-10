from fastapi import FastAPI, WebSockets

app=FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSockets):
    await websocket.accept()
    #await websocket.send_text("Hello, WebSocket!")
    await websocket.close()

@app.post("/register")
async def register_user():
    return {"message":"User registered successfully"}

@app.post("/login")
async def login_user():
    return {"message":"User logged in successfully"}