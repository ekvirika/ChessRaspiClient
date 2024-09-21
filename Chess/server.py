from flask import Flask, request, jsonify, render_template
import threading

app = Flask(__name__)

# Game state
game_state = {
    "current_turn": "white",  # Start with white
    "board": []  # This will store the history of all moves
}

# Lock for managing turn changes
turn_lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/make_move', methods=['POST'])
def make_move():
    global game_state
    data = request.json
    move = data['move']
    player = data['player']

    with turn_lock:
        if player != game_state["current_turn"]:
            return jsonify({"status": "error", "message": "Not your turn"}), 403

        # Process the move (update the board, validate move, etc.)
        game_state['board'].append(move)  # Add move to the board history

        # Switch turns
        game_state["current_turn"] = "black" if player == "white" else "white"

        return jsonify({"status": "success", "move": move, "board": game_state["board"]})

@app.route('/get_move', methods=['GET'])
def get_move():
    global game_state
    
    if game_state['board']:
        last_move = game_state['board'][-1]  # Get the last move
    else:
        last_move = None

    return jsonify({
        "current_turn": game_state["current_turn"], 
        "move": last_move  # Return only the last move
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
