from aiohttp import web, WSMsgType
import json
import time

routes = web.RouteTableDef()
clients = set()
video_state = {
    "videoId": "dQw4w9WgXcQ",  # default video
    "playing": False,
    "currentTime": 0,
    "timestamp": time.time()
}

@routes.get("/")
async def index(request):
    return web.FileResponse('./static/index.html')

@routes.get("/host")
async def host_page(request):
    return web.FileResponse('./static/host.html')

@routes.get("/ws")
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    clients.add(ws)

    # Send current state
    await ws.send_json({"type": "sync", "state": video_state})

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            data = json.loads(msg.data)
            if data.get("type") == "update":
                video_state.update(data["state"])
                for client in clients:
                    if client.closed: continue
                    await client.send_json({"type": "sync", "state": video_state})
        elif msg.type == WSMsgType.ERROR:
            print('WebSocket connection closed with exception %s' % ws.exception())

    clients.discard(ws)
    return ws

app = web.Application()
app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app, port=8080)
