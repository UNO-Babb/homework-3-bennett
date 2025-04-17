#Example Flask App for a hexaganal tile game
#Logic is in this python file

from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# Constants
SAVE_FILE = 'game_state.json'
WIN_SCORE = 5

# Load game state from file or initialize
def load_state():
    if not os.path.exists(SAVE_FILE):
        return {"current_player": 1, "tiles": {}, "winner": None}
    with open(SAVE_FILE, 'r') as f:
        return json.load(f)

# Save game state to file
def save_state(state):
    with open(SAVE_FILE, 'w') as f:
        json.dump(state, f)

@app.route('/')
def index():
    state = load_state()

    # Count tile ownership for score
    scores = {"green": 0, "blue": 0}
    for color in state["tiles"].values():
        if color in scores:
            scores[color] += 1

    return render_template('index.html',
                           tiles=state["tiles"],
                           current_player=state["current_player"],
                           scores=scores,
                           winner=state["winner"]
                           )

@app.route('/add_tile', methods=['POST'])
def add_tile():
    state = load_state()

    # Stop playing if there's a winner
    if state["winner"]:
        return jsonify({"status": "game_over", "winner": state["winner"]})

    # Get click location
    x = request.json['x']
    y = request.json['y']
    key = f"{x},{y}"

    # Prevent overwriting tiles
    if key in state["tiles"]:
        return jsonify({"status": "occupied"})

    # Determine current player color
    color = 'green' if state["current_player"] == 1 else 'blue'
    state["tiles"][key] = color

    # Count tiles
    green_tiles = sum(1 for c in state["tiles"].values() if c == "green")
    blue_tiles = sum(1 for c in state["tiles"].values() if c == "blue")

    # Check win condition
    if green_tiles >= WIN_SCORE:
        state["winner"] = "Player 1"
    elif blue_tiles >= WIN_SCORE:
        state["winner"] = "Player 2"
    else:
        # Switch turn
        state["current_player"] = 2 if state["current_player"] == 1 else 1

    save_state(state)

    return jsonify({
        "status": "ok",
        "color": color,
        "next_player": state["current_player"],
        "winner": state["winner"]
    })

@app.route('/reset', methods=["POST"])
def reset_game():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
    return jsonify({"status": "reset"})

if __name__ == '__main__':
    app.run(debug=True)
