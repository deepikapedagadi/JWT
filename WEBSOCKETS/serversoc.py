# server.py
import asyncio
import websockets

connected_clients = set()

async def handler(websocket):
    # Add the connected client
    connected_clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")
    try:
        asyncio.create_task(send_server_message(websocket))
        async for message in websocket:
            print("Received from client:", message)
            # Send response back
            await websocket.send(f"Server received: {message}")
    except websockets.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    finally:
        connected_clients.remove(websocket)

async def send_server_message(websocket):
    while True:
        await asyncio.sleep(10)
        try:
            await websocket.send("Server says hello")
        except websockets.ConnectionClosed:
            break

async def main():
    server = await websockets.serve(handler, "localhost", 876)
    print("WebSocket server started at ws://localhost:876")
    await server.wait_closed()

asyncio.run(main())
