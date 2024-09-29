import requests, socket, threading
import queue



lichess_token = 'lip_y7xUNHq5PF4WEo7HOECk'
headers = {
    'Authorization': f'Bearer {lichess_token}'
}

class Lichess:
    def __init__(self, queue) -> None:
        self.queue = queue

    # Headers for Lichess API
        
    def run_lichess_handling(self):
        challenge_thread = threading.Thread(target=self.check_challenges_and_events)
        challenge_thread.start()

        game_id = self.get_active_game_id()
        if game_id:
            print(f"Found active game {game_id}")
            # Modify this part of your code
            color = self.get_game_info(game_id)  # This function should return 'white' or 'black
            self.play_game(game_id, color)  # Pass the color as an argument to play_game()
        else:
            print("No active game found. Waiting for challenges...")



    # Get active game ID, used when a game is already in progress
    def get_active_game_id(self):
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
    def accept_challenge(self, challenge_id):
        url = f"https://lichess.org/api/challenge/{challenge_id}/accept"
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            print(f"Challenge {challenge_id} accepted!")
        else:
            print(f"Error accepting challenge: {response.status_code}, {response.text}")


    # Decline a challenge
    def decline_challenge(self, challenge_id):
        url = f"https://lichess.org/api/challenge/{challenge_id}/decline"
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            print(f"Challenge {challenge_id} declined!")
        else:
            print(f"Error declining challenge: {response.status_code}, {response.text}")


    # Listen for new challenges or game events using event streaming
    def check_challenges_and_events(self):
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
                            self.accept_challenge(challenge_id)
                        elif action == 'd':
                            self.decline_challenge(challenge_id)
                        else:
                            print("Invalid input.")
                    elif '"type":"gameStart"' in event:
                        game_id = event.split('"gameId":"')[1].split('"')[0]
                        print(f"Game started: {game_id}")
                        game_thread = threading.Thread(target=self.play_game, args=(game_id, 'black'))
                        game_thread.start()
        else:
            print(f"Error streaming events: {response.status_code}, {response.text}")


    def handle_user_move(self, game_id ):
        user_move = self.queue.get()

        if user_move == 'q':
            print("Quitting game...")
            return
        elif user_move == 'r':
            self.resign_game(game_id)
            return
        elif user_move == 'd':
            self.offer_draw(game_id)
        else:
            self.send_move_to_lichess(game_id, user_move)


    def send_move_to_raspberry_pi(self, move):
        raspberry_pi_ip = '172.20.10.2'  # Replace with your Raspberry Pi's IP
        port = 12383

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((raspberry_pi_ip, port))
            client_socket.settimeout(10)
            # Send the move to the Raspberry Pi
            client_socket.sendall(move.encode())
            print(f"Sent move {move} to Raspberry Pi")

            # client_socket.close()
        except Exception as e:
            print(f"Error sending move to Raspberry Pi: {e}")
        finally:
            # Ensure the socket is always closed after the move is sent
            client_socket.close()
            print("Closed socket connection to Raspberry Pi.")

    def play_game(self, game_id, my_color):
        url = f"https://lichess.org/api/bot/game/stream/{game_id}"
        response = requests.get(url, headers=headers, stream=True)

        if response.status_code == 200:
            moves = []  # To track move history

            for line in response.iter_lines():
                if line:
                    event = line.decode('utf-8')
                    if '"type":"gameState"' in event:
                        new_moves = event.split('"moves":"')[1].split('"')[0].split()

                        # Process only the new moves
                        if len(new_moves) > len(moves):
                            for i in range(len(moves), len(new_moves)):
                                move = new_moves[i]

                                # Classify move based on turn
                                if (i % 2 == 0 and my_color == 'white') or (i % 2 == 1 and my_color == 'black'):
                                    print(f"My move: {move}")
                                else:
                                    print(f"Opponent's move: {move}")
                                    self.send_move_to_raspberry_pi(move)

                            # Update the move list with the latest moves
                            moves = new_moves  
                        
                        # Allow player input when it's their turn
                        if (len(moves) % 2 == 0 and my_color == 'white') or (len(moves) % 2 == 1 and my_color == 'black'):
                            self.handle_user_move(game_id)

        else:
            print(f"Error streaming game: {response.status_code}, {response.text}")

    # Send move to Lichess
    def send_move_to_lichess(self, game_id, move):
        url = f"https://lichess.org/api/bot/game/{game_id}/move/{move}"
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            print(f"Move '{move}' sent successfully!")
        else:
            # Invalid move handling
            print(f"Error sending move: {response.status_code}, {response.text}")
            if response.status_code == 400:
                # Bad request, likely an invalid move
                print(f"Invalid move '{move}'. Please enter a valid move.")
                self.handle_user_move(game_id)  # Prompt the user to enter another move
            else:
                print("An unexpected error occurred. Please try again.")

    #

    # Offer a draw
    def offer_draw(self, game_id):
        url = f"https://lichess.org/api/bot/game/{game_id}/draw/offer"
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            print(f"Draw offer sent for game {game_id}!")
        else:
            print(f"Error offering draw: {response.status_code}, {response.text}")


    # Resign from game
    def resign_game(self, game_id):
        url = f"https://lichess.org/api/bot/game/{game_id}/resign"
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            print(f"Game {game_id} resigned!")
        else:
            print(f"Error resigning game: {response.status_code}, {response.text}")


    # Get game information, including the player's color
    def get_game_info(self, game_id):
        url = f"https://lichess.org/api/bot/game/{game_id}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            color = data.get('color', 'white')  # Default to white if color is not found
            print(f"Your color is: {color}")
            return color
        else:
            print(f"Error getting game info: {response.status_code}, {response.text}")
            return 'black'  # Default to white if there's an error

