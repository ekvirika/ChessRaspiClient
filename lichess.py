import requests
import time
import threading

lichess_token = 'lip_y7xUNHq5PF4WEo7HOECk'

# Headers for Lichess API
headers = {
    'Authorization': f'Bearer {lichess_token}'
}


# Get active game ID, used when a game is already in progress
def get_active_game_id():
    url = "https://lichess.org/api/account/playing"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get('nowPlaying'):
            game_id = data['nowPlaying'][0]['gameId']
            print(f"Active game ID: {game_id}")
            return game_id
        else:
            print("No active games found.")
            return None
    else:
        print(f"Error getting active game: {response.status_code}, {response.text}")
        return None


# Accept a challenge
def accept_challenge(challenge_id):
    url = f"https://lichess.org/api/challenge/{challenge_id}/accept"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print(f"Challenge {challenge_id} accepted!")
    else:
        print(f"Error accepting challenge: {response.status_code}, {response.text}")


# Decline a challenge
def decline_challenge(challenge_id):
    url = f"https://lichess.org/api/challenge/{challenge_id}/decline"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print(f"Challenge {challenge_id} declined!")
    else:
        print(f"Error declining challenge: {response.status_code}, {response.text}")


# Listen for new challenges or game events using event streaming
def check_challenges_and_events():
    url = "https://lichess.org/api/stream/event"

    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                event = line.decode('utf-8')

                if '"type":"challenge"' in event:
                    challenge_id = event.split('"id":"')[1].split('"')[0]
                    print(f"New challenge received: {challenge_id}")
                    action = input("Accept (a) or decline (d) this challenge? (a/d): ").strip().lower()
                    if action == 'a':
                        accept_challenge(challenge_id)
                    elif action == 'd':
                        decline_challenge(challenge_id)
                    else:
                        print("Invalid input.")
                elif '"type":"gameStart"' in event:
                    game_id = event.split('"gameId":"')[1].split('"')[0]
                    print(f"Game started: {game_id}")
                    game_thread = threading.Thread(target=play_game, args=(game_id,))
                    game_thread.start()
    else:
        print(f"Error streaming events: {response.status_code}, {response.text}")


def handle_user_move(game_id):
    user_move = input(
        "Enter your move (e.g., e2e4), 'r' to resign, 'd' to offer a draw, or 'q' to quit: ").strip().lower()

    if user_move == 'q':
        print("Quitting game...")
        return
    elif user_move == 'r':
        resign_game(game_id)
        return
    elif user_move == 'd':
        offer_draw(game_id)
    else:
        send_move_to_lichess(game_id, user_move)


# Stream game moves and handle them in real-time
def play_game(game_id):
    url = f"https://lichess.org/api/bot/game/stream/{game_id}"
    response = requests.get(url, headers=headers, stream=True)

    if response.status_code == 200:
        last_move = None
        for line in response.iter_lines():
            if line:
                event = line.decode('utf-8')
                if '"type":"gameState"' in event:
                    moves = event.split('"moves":"')[1].split('"')[0].split()
                    if moves and moves[-1] != last_move:
                        last_move = moves[-1]
                        print(f"Opponent's move: {last_move}")
                        user_move = input(
                            "Enter your move (e.g., e2e4), 'r' to resign, 'd' to offer a draw, or 'q' to quit: ").strip().lower()
                        if user_move == 'q':
                            print("Quitting game...")
                            break
                        elif user_move == 'r':
                            resign_game(game_id)
                            break
                        elif user_move == 'd':
                            offer_draw(game_id)
                        else:
                            send_move_to_lichess(game_id, user_move)
    else:
        print(f"Error retrieving game stream: {response.status_code}, {response.text}")


# Send move to Lichess
def send_move_to_lichess(game_id, move):
    url = f"https://lichess.org/api/bot/game/{game_id}/move/{move}"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print(f"Move '{move}' sent successfully!")
    else:
        print(f"Error sending move: {response.status_code}, {response.text}")
        play_game(game_id)
#

# Offer a draw
def offer_draw(game_id):
    url = f"https://lichess.org/api/bot/game/{game_id}/draw/offer"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print(f"Draw offer sent for game {game_id}!")
    else:
        print(f"Error offering draw: {response.status_code}, {response.text}")


# Resign from game
def resign_game(game_id):
    url = f"https://lichess.org/api/bot/game/{game_id}/resign"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print(f"Game {game_id} resigned!")
    else:
        print(f"Error resigning game: {response.status_code}, {response.text}")


# Main function
def main():
    challenge_thread = threading.Thread(target=check_challenges_and_events)
    challenge_thread.start()

    game_id = get_active_game_id()
    if game_id:
        print(f"Found active game {game_id}")
        play_game(game_id)
    else:
        print("No active game found. Waiting for challenges...")


if __name__ == "__main__":
    main()
