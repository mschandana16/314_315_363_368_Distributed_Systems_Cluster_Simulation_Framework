import uuid
import time
import json
import os
import subprocess

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

        # Launch Docker container to simulate the node
        subprocess.Popen([
            "docker", "run", "-d",
            "--name", f"node_{node_id[:8]}",
            "-e", f"NODE_ID={node_id}",
            "-e", "API_URL=http://host.docker.internal:5000/heartbeat",
            "node-sim"
        ])

        return node_id

    def update_heartbeat(self, node_id):
        data = self.load_data()
        if node_id in data["nodes"]:
            data["nodes"][node_id]["last_heartbeat"] = time.time()
            self.save_data(data)
            return True
        return False

    def kill_node(self, node_id):
        data = self.load_data()
        if node_id in data["nodes"]:
            container_name = f"node_{node_id[:8]}"
            
            # Kill Docker container
            subprocess.run(["docker", "rm", "-f", container_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Simulate node death by backdating heartbeat
            data["nodes"][node_id]["last_heartbeat"] = time.time() - 99999

            # ❗ DO NOT delete pods here — allow reschedule_pods to handle it
            self.save_data(data)
            return True
        return False

    def get_node_statuses(self, timeout=15):
        data = self.load_data()
        current_time = time.time()

        statuses = {}
        for node_id, info in data["nodes"].items():
            last_beat = info.get("last_heartbeat", 0)
            is_alive = (current_time - last_beat) <= timeout
            statuses[node_id] = {
                "status": "alive" if is_alive else "dead",
                "cpu_cores": info["cpu_cores"],
                "available_cores": info["available_cores"],
                "pods": info["pods"],
                "last_heartbeat": last_beat
            }

        return statuses

    def schedule_pod(self, cpu_required, policy="first_fit"):
        data = self.load_data()
        pod_id = str(uuid.uuid4())
        current_time = time.time()

        candidates = []

        for node_id, node in data["nodes"].items():
            last_beat = node.get("last_heartbeat", 0)
            is_alive = (current_time - last_beat) <= 15
            available = node["available_cores"]

            if is_alive and available >= cpu_required:
                candidates.append((node_id, available))

        if not candidates:
            return {"error": "No alive node with sufficient CPU cores"}

        if policy == "best_fit":
            candidates.sort(key=lambda x: x[1])  # least remaining cores first
        elif policy == "worst_fit":
            candidates.sort(key=lambda x: -x[1])  # most remaining cores first

        chosen_node_id = candidates[0][0]
        chosen_node = data["nodes"][chosen_node_id]
        chosen_node["available_cores"] -= cpu_required
        chosen_node["pods"].append({"pod_id": pod_id, "cpu": cpu_required})

        self.save_data(data)

        return {
            "message": "Pod scheduled",
            "pod_id": pod_id,
            "assigned_node": chosen_node_id
        }

    def get_all_pods(self):
        data = self.load_data()
        all_pods = []

        for node_id, node_info in data["nodes"].items():
            for pod in node_info["pods"]:
                all_pods.append({
                    "pod_id": pod["pod_id"],
                    "cpu": pod["cpu"],
                    "assigned_node": node_id
                })

        return all_pods

    def reschedule_pods(self):
        data = self.load_data()
        current_time = time.time()
        dead_nodes = []
        alive_nodes = {}
        rescheduled_pods = []
        failed_pods = []

        for node_id, node_info in data["nodes"].items():
            last_beat = node_info.get("last_heartbeat", 0)
            if current_time - last_beat > 15:
                dead_nodes.append(node_id)
            else:
                alive_nodes[node_id] = node_info

        for dead_node in dead_nodes:
            dead_node_info = data["nodes"].pop(dead_node)
            for pod in dead_node_info["pods"]:
                cpu_required = pod["cpu"]
                pod_id = pod["pod_id"]
                rescheduled = False

                for node_id, node_info in alive_nodes.items():
                    if node_info["available_cores"] >= cpu_required:
                        node_info["available_cores"] -= cpu_required
                        node_info["pods"].append({
                            "pod_id": pod_id,
                            "cpu": cpu_required
                        })
                        rescheduled_pods.append({
                            "pod_id": pod_id,
                            "from": dead_node,
                            "to": node_id
                        })
                        rescheduled = True
                        break

                if not rescheduled:
                    failed_pods.append({
                        "pod_id": pod_id,
                        "from": dead_node,
                        "cpu": cpu_required,
                        "reason": "Insufficient resources"
                    })

        for node_id in alive_nodes:
            data["nodes"][node_id] = alive_nodes[node_id]

        self.save_data(data)

        return {
            "dead_nodes_removed": dead_nodes,
            "pods_rescheduled": rescheduled_pods,
            "pods_failed": failed_pods
        }

    def auto_scale_and_reschedule(self, default_cpu=4):
        initial = self.reschedule_pods()

        auto_nodes = []
        auto_rescheduled = []

        for p in initial["pods_failed"]:
            pod_id = p["pod_id"]
            cpu_req = p.get("cpu", default_cpu)

            new_node_id = self.add_node(cpu_req)
            auto_nodes.append(new_node_id)

            data = self.load_data()
            node = data["nodes"][new_node_id]
            node["available_cores"] -= cpu_req
            node["pods"].append({"pod_id": pod_id, "cpu": cpu_req})
            self.save_data(data)

            auto_rescheduled.append({
                "pod_id": pod_id,
                "assigned_node": new_node_id
            })

        return {
            "initial_reschedule": initial,
            "auto_scaled_nodes": auto_nodes,
            "auto_rescheduled_pods": auto_rescheduled
        }

    def get_all_nodes(self):
        data = self.load_data()
        return data["nodes"]
