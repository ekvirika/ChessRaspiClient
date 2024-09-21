import berserk
token = 'lip_e40tkYVdBFHOdocl6K6V'

session = berserk.TokenSession(token)
client = berserk.Client(session=session)

# Fetch the list of games
games = client.games.export_by_player('your_bot_username')
for game in games:
    game_id = game['id']
    break  # Use the first game; you might want to handle multiple games

# Example move; replace with your actual move
move = 'e2e4'  # Move notation (e.g., move from e2 to e4)

# Make the move
client.bots.make_move(game_id, move)

print(f"Moved {move} in game {game_id}")