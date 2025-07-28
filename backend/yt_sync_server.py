import asyncio
import websockets
import json
import os

PORT = int(os.environ.get("PORT", 8765))
connected = set()
current_state = {
    "videoId": "dQw4w9WgXcQ",
    "playing": False,
    "currentTime": 0,
    "timestamp": 0
}

async def handler(websocket, path):
    connected.add(websocket)
    try:
        await websocket.send(json.dumps({"type": "sync", "state": current_state}))
        async for message in websocket:
            msg = json.loads(message)
            if msg["type"] == "update":
                global current_state
                current_state = msg["state"]
                await broadcast()
    finally:
        connected.remove(websocket)

async def broadcast():
    if connected:
        message = json.dumps({"type": "sync", "state": current_state})
        await asyncio.gather(*[ws.send(message) for ws in connected])

async def main():
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
