import asyncio
import websockets
import jwt

SECRET_KEY = "mysecret"  # must match client token generator

async def handler(websocket):
    try:
        # 1. First message from client must be JWT
        token = await websocket.recv()
        print("Received token:", token)

        # 2. Verify JWT
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            username = payload["user"]
            print(f"✅ Authenticated user: {username}")
            await websocket.send(f"Welcome {username}! You are authenticated.")
        except jwt.ExpiredSignatureError:
            await websocket.send("❌ Token expired. Please login again.")
            return
        except jwt.InvalidTokenError:
            await websocket.send("❌ Invalid token.")
            return

        # 3. Continue chatting after authentication
        async for message in websocket:
            print(f"{username} says:", message)
            await websocket.send(f"Echo: {message}")

    except websockets.ConnectionClosed:
        print("🔌 Connection closed")

async def main():
    async with websockets.serve(handler, "localhost", 100):
        print("Server running at ws://localhost:100")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
