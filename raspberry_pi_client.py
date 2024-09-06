# raspberry_pi_client.py (Run this on your Raspberry Pi)

import time
import requests

API_SERVER_IP = '192.168.0.102'
API_SERVER_PORT = '8000'
# API_SERVER = 'http://{API_SERVER_IP}:{API_SERVER_PORT}'
API_SERVER = "http://192.168.0.102:8000"


def get_current_turn():
    response = requests.get(f"{API_SERVER}/get_move")
    return response.json()

def send_move_to_server(move):
    data = {"move": move, "player": "black"}
    response = requests.post(f"{API_SERVER}/make_move", json=data)
    return response.json()

while True:
    game_state = get_current_turn()
    if game_state['current_turn'] == 'black':
        # Generate or receive the move (for now, we just use a placeholder)
        move = input("input your move:")
        response = send_move_to_server(move)
        print("Move sent:", response)
    else:
        print("waiting....")
    time.sleep(1)









