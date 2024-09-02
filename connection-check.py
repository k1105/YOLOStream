import asyncio
import websockets

async def listen():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                message = await websocket.recv()
                print(f"Received message: {message}")
            except websockets.ConnectionClosed:
                print("Connection closed")
                break

asyncio.get_event_loop().run_until_complete(listen())
