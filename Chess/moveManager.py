from Helpers.ChessboardController import ChessboardController

def main():
    # Example of usage:
    controller = ChessboardController(mainsail_url="http://your-mainsail-url", electromagnet_pin=3)
    while True:
        move = input("your move: ")
        if move == 'q':
            break
        controller.make_move("move")


if __name__ == "__main__":
    main()