import asyncio
import websockets

async def websocket_client():
    """Client to connect to the WebSocket server."""
    uri = "ws://localhost:8765"  # WebSocket server URI
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to the WebSocket server.")
            
            # Example: Send a message to the server
            message = "Hello, server!"
            await websocket.send(message)
            print(f"Sent message: {message}")
            
            # Example: Receive a response from the server
            response = await websocket.recv()
            print(f"Received response: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(websocket_client())