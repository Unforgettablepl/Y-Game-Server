from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime, timedelta
from threading import Timer

app = Flask(__name__)
CORS(app)

# In-memory databases
parties = {}
party_timestamps = {}

# Helper function to clean up old party codes
def cleanup_parties():
    current_time = datetime.now()
    to_delete = [code for code, timestamp in party_timestamps.items() if current_time - timestamp > timedelta(hours=24)]
    for code in to_delete:
        del parties[code]
        del party_timestamps[code]
    Timer(3600, cleanup_parties).start()

# Start the cleanup timer
cleanup_parties()

@app.route('/api/createParty', methods=['GET'])
def create_party():
    party_code = uuid.uuid4().hex
    while party_code in parties:
        party_code = uuid.uuid4().hex
    parties[party_code] = {'last_move': 0, 'last_player': 0}
    party_timestamps[party_code] = datetime.now()
    return jsonify({'partyCode': party_code})

@app.route('/api/getPlayerID', methods=['GET'])
def get_player_id():
    party_code = request.args.get('partyCode')
    if party_code not in parties:
        return jsonify({'playerId': 0})
    parties[party_code]['last_player'] += 1
    return jsonify({'playerId': parties[party_code]['last_player']})

@app.route('/api/getMove', methods=['GET'])
def get_move():
    party_code = request.args.get('partyCode')
    if party_code not in parties:
        return jsonify({'error': 'Invalid party code'}), 400
    return jsonify({'nodeId': parties[party_code]['last_move']})

@app.route('/api/pushMove', methods=['POST'])
def push_move():
    data = request.json
    party_code = data.get('partyCode')
    node_id = data.get('nodeId')
    if party_code not in parties:
        return jsonify({'error': 'Invalid party code'}), 400
    parties[party_code]['last_move'] = node_id
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
