import asyncio
import json
import os
from aiohttp import web

PORT = int(os.environ.get("PORT", 10000))

connected = set()
current_state = {
    "videoId": "dQw4w9WgXcQ",
    "playing": False,
    "currentTime": 0,
    "timestamp": 0
}

routes = web.RouteTableDef()

@routes.get("/")
async def index(request):
    return web.FileResponse('./static/index.html')

@routes.get('/ws')
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    connected.add(ws)
    await ws.send_json({"type": "sync", "state": current_state})

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = json.loads(msg.data)
            if data["type"] == "update":
                global current_state
                current_state = data["state"]
                await broadcast()
        elif msg.type == web.WSMsgType.ERROR:
            print("WebSocket error:", ws.exception())

    connected.remove(ws)
    return ws

async def broadcast():
    for ws in connected:
        await ws.send_json({"type": "sync", "state": current_state})

app = web.Application()
app.add_routes(routes)
app.router.add_static('/', path='./static', name='static')

if __name__ == '__main__':
    web.run_app(app, port=PORT)
