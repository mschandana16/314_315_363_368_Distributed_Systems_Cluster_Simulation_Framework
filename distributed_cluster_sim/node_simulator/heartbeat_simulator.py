import time
import requests

BASE_URL = "http://127.0.0.1:5000"

def get_all_nodes():
    try:
        res = requests.get(f"{BASE_URL}/nodes")
        return list(res.json().get("nodes", {}).keys())
    except Exception as e:
        print("❌ Error fetching nodes:", e)
        return []

def send_heartbeat(node_id):
    try:
        res = requests.post(f"{BASE_URL}/heartbeat", json={"node_id": node_id})
        if res.status_code == 200:
            print(f"[✔] Heartbeat sent for {node_id}")
        else:
            print(f"[✖] Failed for {node_id}: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[!] Exception for {node_id}: {e}")

if __name__ == "__main__":
    print("🚀 Starting multi-node heartbeat simulator...")
    while True:
        node_ids = get_all_nodes()
        for node_id in node_ids:
            send_heartbeat(node_id)
        time.sleep(5)
