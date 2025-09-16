import asyncio
import websockets

# Paste the JWT token you generated here
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZGVlcGlrYSIsImV4cCI6MTc1Njk3NTkyMX0.0aiwIYLIYUY1pHWTyK-AFkgBn3gH8LF7sHsZKLK1_0M"

async def main():
    uri = "ws://localhost:100"
    async with websockets.connect(uri) as websocket:
        # 1. Send JWT token first
        await websocket.send(TOKEN)
        auth_reply = await websocket.recv()
        print("Server:", auth_reply)

        if "❌" in auth_reply:
            return  # stop if authentication failed

        # 2. Start chatting
        print("Type messages (type 'exit' to quit):")
        while True:
            msg = input("> ")
            if msg.lower() == "exit":
                print("Closing connection...")
                break
            await websocket.send(msg)
            reply = await websocket.recv()
            print("Server:", reply)

if __name__ == "__main__":
    asyncio.run(main())
