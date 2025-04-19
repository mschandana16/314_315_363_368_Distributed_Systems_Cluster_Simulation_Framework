import requests
import time
import os

API_URL = os.environ.get("API_URL", "http://host.docker.internal:5000/heartbeat")
NODE_ID = os.environ.get("NODE_ID")

if not NODE_ID:
    raise Exception("NODE_ID not set")

while True:
    try:
        response = requests.post(API_URL, json={"node_id": NODE_ID})
        print(f"[Heartbeat] Sent for node {NODE_ID} — {response.status_code}")
    except Exception as e:
        print(f"[Heartbeat Error] {e}")
    time.sleep(5)  # send every 5 seconds
