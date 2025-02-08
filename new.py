import os
import stat
import chess
import chess.engine
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

STOCKFISH_PATH = "/opt/render/project/src/Stock_fish"

# Ensure Stockfish is executable
if not os.access(STOCKFISH_PATH, os.X_OK):
    os.chmod(STOCKFISH_PATH, os.stat(STOCKFISH_PATH).st_mode | stat.S_IEXEC)

print("Stockfish is now executable:", os.access(STOCKFISH_PATH, os.X_OK))

# Start Stockfish
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
board = chess.Board()

# Convert move to row & column
def move_to_row_col(move):
    start_square, end_square = move[:2], move[2:]

    def chess_notation_to_indices(square):
        return 8 - int(square[1]), ord(square[0]) - ord('a')

    return (*chess_notation_to_indices(start_square), *chess_notation_to_indices(end_square))

# Homepage Route
@app.route("/")
def home():
    return "Stockfish Chess Engine is Running!"

@app.route('/get_best_move', methods=['POST'])
def get_best_move():
    try:
        data = request.get_json()
        if not data or 'turn' not in data:
            return jsonify({'error': 'Invalid input, send {"turn": "W"} or {"turn": "B"}'}), 400

        if data['turn'] not in ['W', 'B']:
            return jsonify({'error': 'Invalid turn value'}), 400
        
        # Ensure AI's turn before moving
        if (data['turn'] == 'W' and board.turn == chess.BLACK) or (data['turn'] == 'B' and board.turn == chess.WHITE):
            result = engine.play(board, chess.engine.Limit(time=2.0))
            best_move = result.move.uci()
            board.push(result.move)

            start_r, start_c, end_r, end_c = move_to_row_col(best_move)
            return jsonify({'start_row': start_r, 'start_col': start_c, 'end_row': end_r, 'end_col': end_c})

        return jsonify({'message': "Not AI's turn"}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

# Close Stockfish
@app.route('/close_engine', methods=['GET'])
def close_engine():
    engine.quit()
    return "Engine Closed"

# Run Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
