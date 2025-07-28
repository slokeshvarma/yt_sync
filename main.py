from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import time

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

video_state = {
    "videoId": "dQw4w9WgXcQ",
    "playlistId": None,
    "playing": False,
    "currentTime": 0,
    "timestamp": time.time()
}

clients = []

@app.get("/")
async def get_root():
    return FileResponse("static/index.html")

@app.get("/host")
async def get_host():
    return FileResponse("static/host.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global video_state
    await websocket.accept()
    clients.append(websocket)
    try:
        await websocket.send_json({"type": "sync", "state": video_state})
        while True:
            data = await websocket.receive_json()
            if data["type"] == "update":
                video_state = data["state"]
                for client in clients:
                    if client != websocket:
                        await client.send_json({"type": "sync", "state": video_state})
    except WebSocketDisconnect:
        clients.remove(websocket)
