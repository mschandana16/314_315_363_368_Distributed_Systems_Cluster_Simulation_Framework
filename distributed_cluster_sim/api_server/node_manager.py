import uuid
import time
import json
import os

class NodeManager:
    def __init__(self):
        self.data_file = os.path.join(os.path.dirname(__file__), "data_store.json")
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump({"nodes": {}}, f)

    def load_data(self):
        with open(self.data_file, 'r') as f:
            return json.load(f)

    def save_data(self, data):
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)

    def add_node(self, cpu_cores):
        data = self.load_data()
        node_id = str(uuid.uuid4())
        data["nodes"][node_id] = {
            "cpu_cores": cpu_cores,
            "available_cores": cpu_cores,
            "pods": [],
            "last_heartbeat": time.time()
        }
        self.save_data(data)
        return node_id

    def update_heartbeat(self, node_id):
        data = self.load_data()
        if node_id in data["nodes"]:
            data["nodes"][node_id]["last_heartbeat"] = time.time()
            self.save_data(data)
            return True
        return False




    def get_all_nodes(self):
        data = self.load_data()
        return data["nodes"]
