import time, Board, SendMove, Electromagnet
class ChessboardController:
    def __init__(self, klipper_host, klipper_port, electromagnet_pin):
        self.board = Board()
        self.klipper = SendMove(klipper_host, klipper_port)
        self.electromagnet = Electromagnet(electromagnet_pin)

    def make_move(self, uci_move):
        """Executes a move on the physical chessboard based on UCI move format e.g., 'e2e4'"""
        start_square = uci_move[:2]
        end_square = uci_move[2:]

        # Get the Klipper coordinates for the start and end squares
        start_coords = self.board.get_klipper_coords(start_square)
        end_coords = self.board.get_klipper_coords(end_square)

        if start_coords and end_coords:
            # Move to start square
            self.klipper.move_to(*start_coords)

            # Activate electromagnet to pick up the piece
            self.electromagnet.activate()
            time.sleep(1)  # Short delay to ensure piece is magnetized

            # Move to the end square along a "safe path" (you could define this path manually)
            self.klipper.move_to(*end_coords)

            # Deactivate electromagnet to drop the piece
            self.electromagnet.deactivate()
            time.sleep(1)  # Short delay to ensure piece is dropped

        else:
            print("Invalid UCI move or coordinates not found!")
