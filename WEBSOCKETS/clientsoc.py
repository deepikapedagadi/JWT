# client.py
import asyncio
import websockets

async def client():
    uri = "ws://localhost:876"
    async with websockets.connect(uri) as websocket:
        print("Connected to server!")

        # Start a background task to listen to server
        asyncio.create_task(listen_server(websocket))

        while True:
            msg = input("You: ")
            await websocket.send(msg)

async def listen_server(websocket):
    try:
        async for message in websocket:
            print("Server:", message)
    except websockets.ConnectionClosed:
        print("Connection closed by server")

asyncio.run(client())
