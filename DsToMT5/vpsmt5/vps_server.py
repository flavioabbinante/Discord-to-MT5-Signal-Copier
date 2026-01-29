from flask import Flask, request, jsonify
import mt5_manager
import config_vps

app = Flask(__name__)

def check_auth():
    """Validates the API key from the request headers."""
    return request.headers.get("X-API-KEY") == config_vps.API_KEY_VPS

@app.route('/trade', methods=['POST'])
def handle_trade():
    """Endpoint for opening new trades."""
    if not check_auth():
        return jsonify({"status": "Unauthorized"}), 401
    
    data = request.json
    result = mt5_manager.apri_operazione(
        data['simbolo'], 
        data['tipo'], 
        data['sl'], 
        data['tp']
    )
    return jsonify({"status": result.comment, "retcode": result.retcode})

@app.route('/close', methods=['POST'])
def handle_close():
    """Endpoint for closing existing trades."""
    if not check_auth():
        return jsonify({"status": "Unauthorized"}), 401
    
    data = request.json
    count = mt5_manager.chiudi_operazioni_simbolo(data['simbolo'])
    return jsonify({"status": "Closed", "count": count})

if __name__ == '__main__':
    # Initialize MT5 before starting the web server
    if mt5_manager.inizializza_mt5():
        # Running on 0.0.0.0 makes the server accessible from the public IP
        # Ensure Port 5000 is open in the Windows Firewall
        app.run(host='0.0.0.0', port=5000)