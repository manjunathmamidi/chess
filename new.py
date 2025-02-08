import os
from flask import Flask, jsonify, request
import chess
import chess.engine
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# List of possible Stockfish paths
STOCKFISH_PATHS = [
    os.environ.get("STOCKFISH_PATH", ""),  # Render environment variable
    "/opt/render/project/src/stockfish/stockfish-windows-x86-64-avx2.exe",
    "/opt/render/project/src/stockfish/stockfish-linux-x86-64-avx2",
    "./stockfish-windows-x86-64-avx2.exe",
    "./stockfish-linux-x86-64-avx2",
]

# Find a valid Stockfish path
def find_stockfish():
    for path in STOCKFISH_PATHS:
        if path and os.path.exists(path) and os.access(path, os.X_OK):
            return path
    raise FileNotFoundError("Stockfish not found in any of the expected locations.")

# Get correct Stockfish path
STOCKFISH_PATH = find_stockfish()

# Initialize Stockfish engine
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
board = chess.Board()

# Convert move to row & column
def move_to_row_col(move):
    start_square, end_square = move[:2], move[2:]

    def chess_notation_to_indices(square):
        return 8 - (int(square[1]) - 1), ord(square[0]) - ord('a') + 1

    return (*chess_notation_to_indices(start_square), *chess_notation_to_indices(end_square))

# Route to get the best move
@app.route('/get_best_move', methods=['POST'])
def get_best_move():
    data = request.json
    if 'turn' not in data or data['turn'] not in ['W', 'B']:
        return jsonify({'error': 'Invalid input, send "W" for White or "B" for Black'}), 400

    if (data['turn'] == 'W' and board.turn == chess.BLACK) or (data['turn'] == 'B' and board.turn == chess.WHITE):
        result = engine.play(board, chess.engine.Limit(time=2.0))
        best_move = result.move.uci()
        board.push(result.move)
        start_r, start_c, end_r, end_c = move_to_row_col(best_move)

        return jsonify({'start_row': start_r, 'start_col': start_c, 'end_row': end_r, 'end_col': end_c})

    return jsonify({'message': "Not AI's turn"}), 200

# Route to close Stockfish engine
@app.route('/close_engine', methods=['GET'])
def close_engine():
    engine.quit()
    return "Engine Closed"

# Run Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
