import asyncio
import websockets

async def handler(websocket):
    async for message in websocket:
        print("Client says:", message)

        # Simple reply logic
        if message.lower() == "hi":
            reply = "Hello! How can I help you?"
        else:
            reply = f"You said: {message}"

        await websocket.send(reply)

async def main():
    async with websockets.serve(handler, "localhost", 9000):  # use port 9000
        print("Server running at ws://localhost:9000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
