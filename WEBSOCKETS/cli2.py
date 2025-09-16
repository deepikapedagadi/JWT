import asyncio
import websockets

async def main():
    uri = "ws://localhost:9000"
    async with websockets.connect(uri) as websocket:
        print("Connected to server. Type 'exit' to quit.")
        while True:
            msg = input("> ")
            if msg.lower() == "exit":
                print("Closing connection...")
                break
            await websocket.send(msg)
            reply = await websocket.recv()
            print("Server replied:", reply)

if __name__ == "__main__":
    asyncio.run(main())
