import requests
import os

BASE_URL = "http://127.0.0.1:8000"

# 1. Login
print("Logging in...")
login_data = {
    "username": "test1@example.com",
    "password": "pass123"
}
try:
    res = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    res.raise_for_status()
    token = res.json()["access_token"]
    print("Logged in successfully!")
except Exception as e:
    # If login fails, let's register
    print("Login failed, attempting register...")
    reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": "test1@example.com",
        "password": "pass123"
    })
    print("Register status:", reg_res.status_code)
    res = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    token = res.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}"
}

# 2. List documents
res = requests.get(f"{BASE_URL}/api/documents", headers=headers)
docs = res.json()
print(f"Current documents: {len(docs)}")

if docs:
    # Find one document to delete that exists
    target_doc = docs[0]
    doc_id = target_doc["id"]
    doc_name = target_doc["name"]
    print(f"Attempting to delete first document: {doc_id} ({doc_name})")
    
    # 3. Call delete
    del_res = requests.delete(f"{BASE_URL}/api/documents/bulk", headers=headers, json={"ids": [doc_id]})
    print("Delete response status:", del_res.status_code)
    print("Delete response JSON:", del_res.json())
else:
    print("No documents to delete.")
