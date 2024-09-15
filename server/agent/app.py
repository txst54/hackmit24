from fastapi import FastAPI
from fastapi import WebSocket

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.websocket("/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Replace this with your code to send logs
        await websocket.send_text("Log message")