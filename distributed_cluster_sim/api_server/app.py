from flask import Flask, request, jsonify, render_template
from node_manager import NodeManager

app = Flask(__name__)
node_manager = NodeManager()

# GET all nodes
@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify({"nodes": node_manager.get_all_nodes()}), 200

@app.route('/node_status', methods=['GET'])
def node_status():
    statuses = node_manager.get_node_statuses()
    return jsonify({"node_statuses": statuses}), 200

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
    
@app.route('/kill_node/<node_id>', methods=['POST'])
def kill_node(node_id):
    success = node_manager.kill_node(node_id)
    if success:
        return jsonify({"message": f"Node {node_id} marked as dead and pods removed"}), 200
    else:
        return jsonify({"error": "Node not found"}), 404

    
@app.route('/launch_pod', methods=['POST'])
def launch_pod():
    data = request.get_json()
    cpu_required = data.get("cpu_required")
    policy = data.get("policy", "first_fit")  # default fallback

    if cpu_required is None:
        return jsonify({"error": "CPU requirement not specified"}), 400

    result = node_manager.schedule_pod(cpu_required, policy)

    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201


@app.route('/pods', methods=['GET'])
def list_pods():
    pods = node_manager.get_all_pods()
    return jsonify({"pods": pods}), 200

@app.route('/reschedule_pods', methods=['POST'])
def reschedule_pods():
    result = node_manager.reschedule_pods()
    return jsonify(result), 200

@app.route('/auto_scale', methods=['POST'])
def auto_scale():
    result = node_manager.auto_scale_and_reschedule(default_cpu=4)
    return jsonify(result), 200

@app.route('/')
def dashboard():
    nodes = node_manager.get_node_statuses()
    pods = node_manager.get_all_pods()
    return render_template('index.html', nodes=nodes, pods=pods)




if __name__ == '__main__':
    app.run(debug=True, port=5000)
