# client.py
import asyncio
import websockets

async def main():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print("Connected to server. Type messages (type 'exit' to quit).")
        while True:
            msg = input("> ")  # get user input
            if msg.lower() == "exit":
                print("Closing connection...")
                break
            await websocket.send(msg)          # send to server
            reply = await websocket.recv()     # wait for reply
            print("Server replied:", reply)

if __name__ == "__main__":
    asyncio.run(main())
