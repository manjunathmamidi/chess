import os
import chess
import chess.engine
import stat
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

STOCKFISH_PATH = "/opt/render/project/src/Stock_fish"

# Ensure Stockfish is executable
if not os.access(STOCKFISH_PATH, os.X_OK):
    os.chmod(STOCKFISH_PATH, os.stat(STOCKFISH_PATH).st_mode | stat.S_IEXEC)

# Debugging print
print("Stockfish Executable:", os.access(STOCKFISH_PATH, os.X_OK))

# Start Stockfish Engine
try:
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    print("Stockfish Engine Started Successfully!")
except Exception as e:
    print("Error starting Stockfish:", e)

board = chess.Board()

@app.route("/")
def home():
    return "Stockfish Chess Engine is Running!"

@app.route('/get_best_move', methods=['POST'])
def get_best_move():
    data = request.json

    if 'turn' not in data or data['turn'] not in ['W', 'B']:
        return jsonify({'error': 'Invalid input, send "W" for White or "B" for Black'}), 400

    try:
        if (data['turn'] == 'W' and board.turn == chess.WHITE) or (data['turn'] == 'B' and board.turn == chess.BLACK):
            result = engine.play(board, chess.engine.Limit(time=0.05, depth=3))  # Reduce time & depth
            best_move = result.move.uci()
            board.push(result.move)

            return jsonify({'best_move': best_move})
        else:
            return jsonify({'message': "Not AI's turn"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': "Internal Server Error"}), 500

@app.route('/close_engine', methods=['GET'])
def close_engine():
    engine.quit()
    return "Engine Closed"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
