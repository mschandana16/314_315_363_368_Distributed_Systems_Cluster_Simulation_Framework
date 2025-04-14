from flask import Flask, request, jsonify
from node_manager import NodeManager

app = Flask(__name__)
node_manager = NodeManager()

# GET all nodes
@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify({"nodes": node_manager.get_all_nodes()}), 200


@app.route('/register_node', methods=['POST'])
def register_node():
    data = request.get_json()
    # do something with data
    return jsonify({"message": "Node registered"})


# POST to add a new node
@app.route('/add_node', methods=['POST'])
def add_node():
    data = request.json
    cpu_cores = data.get("cpu_cores")
    if cpu_cores is None:
        return jsonify({"error": "CPU cores not specified"}), 400
    node_id = node_manager.add_node(cpu_cores)
    return jsonify({"message": "Node added", "node_id": node_id}), 201

# POST to simulate a heartbeat
@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    node_id = data.get("node_id")
    # if not node_id:
    #     return jsonify({"error": "Node ID required"}), 400

    if not node_id:
        print(f"ERROR: node_id is missing or null. Payload: {data}")
        return jsonify({"error": "Node ID required"}), 400


    print(f"Received heartbeat for node_id: {node_id}")  #debug line

    updated = node_manager.update_heartbeat(node_id)
    print(f"Update status: {updated}")  # debug line

    if updated:
        return jsonify({"message": "Heartbeat received"}), 200
    else:
        return jsonify({"error": "Node not found"}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
