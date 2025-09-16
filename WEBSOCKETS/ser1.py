# server.py
import asyncio
import websockets

async def handler(websocket):
    async for message in websocket:
        print("Client says:", message)
        await websocket.send("Echo: " + message)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Server running at ws://localhost:8765")
        await asyncio.Future()  # keep running

if __name__ == "__main__":
    asyncio.run(main())
