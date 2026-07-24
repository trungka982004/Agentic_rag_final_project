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
    parser = argparse.ArgumentParser(description="Test websocket chat with multiple concurrent clients")
    parser.add_argument("--clients", type=int, default=3, help="Number of concurrent clients to test")
    args = parser.parse_args()

    num_clients = args.clients
    print(f"Testing with {num_clients} concurrent clients...")
    
    tasks = []
    for i in range(1, num_clients + 1):
        tasks.append(test_concurrent_chat(i, f"test{i}@example.com", f"pass123_{i}"))
        
    await asyncio.gather(*tasks)
    print("Test completed.")

if __name__ == "__main__":
    import argparse
    asyncio.run(main())
