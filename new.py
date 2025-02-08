import os
import stat
from flask import Flask, jsonify, request
import chess
import chess.engine
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Set correct path for Stockfish
STOCKFISH_PATH = "/opt/render/project/src/Stock_fish"

# Grant execution permission to Stockfish
os.chmod(STOCKFISH_PATH, os.stat(STOCKFISH_PATH).st_mode | stat.S_IEXEC)

# Initialize Stockfish engine
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
board = chess.Board()

# Convert move to row & column format
def move_to_row_col(move):
    start_square, end_square = move[:2], move[2:]

    def chess_notation_to_indices(square):
        return 8 - int(square[1]), ord(square[0]) - ord('a')

    return (*chess_notation_to_indices(start_square), *chess_notation_to_indices(end_square))

# Home route
@app.route("/")
def home():
    return "Stockfish Chess Engine is Running!"

# Get best move from Stockfish (Now AI always plays)
@app.route('/get_best_move', methods=['POST'])
def get_best_move():
    try:
        data = request.get_json()
        if not data or 'turn' not in data:
            return jsonify({'error': 'Invalid input, send {"turn": "W"} or {"turn": "B"}'}), 400

        # Generate best move
        result = engine.play(board, chess.engine.Limit(time=2.0))
        best_move = result.move.uci()
        board.push(result.move)

        # Convert move to frontend format
        start_r, start_c, end_r, end_c = move_to_row_col(best_move)
        return jsonify({'start_row': start_r, 'start_col': start_c, 'end_row': end_r, 'end_col': end_c})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

# Close Stockfish engine route
@app.route('/close_engine', methods=['GET'])
def close_engine():
    engine.quit()
    return "Engine Closed"

# Run Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
