# server.py
import asyncio
import websockets

async def welcome(websocket):
    async for msg in websocket:
        print("Client says:", msg)
        await websocket.send("Echo: " + msg)

async def main():
    async with websockets.serve(welcome, "localhost", 8765):
        print("Server is running")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())

