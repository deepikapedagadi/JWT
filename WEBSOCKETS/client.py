import asyncio
import websockets

async def client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print("Connected to server")

        while True:
            message = input("Enter message to send (or 'exit' to quit): ")
            if message.lower() == 'exit':
                print("Closing connection...")
                break

            await websocket.send(message)
            print(f"Sent: {message}")

            response = await websocket.recv()
            print(f"Received: {response}")

asyncio.run(client())
