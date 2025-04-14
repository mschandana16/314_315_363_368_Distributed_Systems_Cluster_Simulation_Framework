import time
import requests
import uuid
import os

# API_URL = os.environ.get("API_URL", "http://host.docker.internal:5000")
API_URL = "http://host.docker.internal:5000"

def register_node(cpu_cores):
    res = requests.post(f"{API_URL}/add_node", json={"cpu_cores": cpu_cores})
    return res.json().get("node_id")

def send_heartbeat(node_id):
    requests.post(f"{API_URL}/heartbeat", json={"node_id": node_id})

if __name__ == "__main__":
    cpu_cores = 4  # Or get from ENV
    node_id = register_node(cpu_cores)
    print(f"Node registered with ID: {node_id}")
    while True:
        send_heartbeat(node_id)
        print(f"Heartbeat sent from {node_id}")
        time.sleep(5)
