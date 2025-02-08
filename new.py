import os
import stat
import chess
import chess.engine
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
CORS(app)

# Path to Stockfish binary (Ensure it's in the correct location)
STOCKFISH_PATH = "/opt/render/project/src/Stock_fish"

# Ensure Stockfish has execute permissions
os.chmod(STOCKFISH_PATH, os.stat(STOCKFISH_PATH).st_mode | stat.S_IEXEC)

# Initialize Stockfish engine
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
board = chess.Board()

# Convert move to row & column
def move_to_row_col(move):
    start_square, end_square = move[:2], move[2:]

    def chess_notation_to_indices(square):
        return 8 - int(square[1]), ord(square[0]) - ord('a')

    return (*chess_notation_to_indices(start_square), *chess_notation_to_indices(end_square))

# ✅ Serve `index.html` (Frontend)
@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

# ✅ Serve static files like `p3.css` & `p3.js`
@app.route("/<path:filename>")
def serve_static_files(filename):
    return send_from_directory(".", filename)

# ✅ AI Move Endpoint
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

# ✅ Route to Close Stockfish Engine
@app.route('/close_engine', methods=['GET'])
def close_engine():
    engine.quit()
    return "Engine Closed"

# ✅ Run Flask App
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
