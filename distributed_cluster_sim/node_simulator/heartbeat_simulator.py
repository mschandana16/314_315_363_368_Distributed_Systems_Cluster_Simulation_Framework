import time
import requests

# Replace this with the actual node_id you get from /add_node
NODE_ID = "0b3dd1c4-9fca-4bab-b1cc-492fb12f33fa"
API_URL = "http://127.0.0.1:5000/heartbeat"

def send_heartbeat():
    try:
        res = requests.post(API_URL, json={"node_id": NODE_ID})
        if res.status_code == 200:
            print(f"[✔] Heartbeat sent: {res.json()}")
        else:
            print(f"[✖] Heartbeat failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[!] Error sending heartbeat: {e}")

if __name__ == "__main__":
    print(f"🚀 Starting heartbeat simulator for node: {NODE_ID}")
    while True:
        send_heartbeat()
        time.sleep(5)  # Send heartbeat every 5 seconds
