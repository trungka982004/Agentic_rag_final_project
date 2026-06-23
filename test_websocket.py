import asyncio
import httpx
import websockets
import json

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000"

async def test_concurrent_chat(client_id, email, password):
    print(f"Client {client_id}: Starting...")
    async with httpx.AsyncClient() as client:
        # Register or Login
        res = await client.post(f"{BASE_URL}/api/auth/register", json={"email": email, "password": password})
        if res.status_code == 400:
            pass # Already registered
        
        # Login
        res = await client.post(f"{BASE_URL}/api/auth/login", data={"username": email, "password": password})
        token = res.json()["access_token"]
        
        # Create Session
        headers = {"Authorization": f"Bearer {token}"}
        res = await client.post(f"{BASE_URL}/api/sessions", json={"title": f"Test {client_id}"}, headers=headers)
        session_id = res.json()["id"]
        
        print(f"Client {client_id}: Logged in, session created: {session_id}")
        
        # Connect to WS
        uri = f"{WS_URL}/api/ws/chat/{session_id}?token={token}"
        async with websockets.connect(uri) as websocket:
            print(f"Client {client_id}: Connected to WS")
            
            # Send message
            query = f"Write a small poem about AI. Make it short."
            await websocket.send(json.dumps({"question": query}))
            
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                
                if data["type"] == "node_update":
                    print(f"Client {client_id}: Node updated -> {data['node']}")
                elif data["type"] == "final_answer":
                    print(f"Client {client_id}: Got final answer! Length: {len(data['content'])}")
                    break
                elif data["type"] == "error":
                    print(f"Client {client_id}: ERROR -> {data['message']}")
                    break
                else:
                    print(f"Client {client_id}: {data['type']}")

async def main():
    print("Testing with 1 client...")
    await test_concurrent_chat(1, "test1@example.com", "pass123")
    print("Test completed.")

if __name__ == "__main__":
    asyncio.run(main())
