import time
import requests  # To send HTTP requests to Mainsail
from Board import Board  # Assuming you have the Board class defined in a file named board.py
from Electromagnet import Electromagnet  # Assuming Electromagnet class is defined similarly

class ChessboardController:
    def __init__(self, mainsail_url, electromagnet_pin):
        self.board = Board()
        self.mainsail_url = mainsail_url
        self.electromagnet = Electromagnet(electromagnet_pin)

    def send_gcode(self, gcode):
        """Send a G-code command to the Mainsail API."""
        url = f"{self.mainsail_url}/printer/gcode/script"
        headers = {'Content-Type': 'application/json'}
        payload = {'script': gcode}

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an error for bad status codes
        except requests.RequestException as e:
            print(f"Error sending G-code to Mainsail: {e}")
        else:
            print(f"G-code sent successfully: {gcode}")

    def make_move(self, uci_move):
        """Executes a move on the physical chessboard based on UCI move format e.g., 'e2e4'"""
        start_square = uci_move[:2]
        end_square = uci_move[2:]

        # Get the Klipper coordinates for the start and end squares
        start_coords = self.board.get_klipper_coords(start_square)
        end_coords = self.board.get_klipper_coords(end_square)

        if start_coords and end_coords:
            # Move to the start square
            gcode_start = f"G1 X{start_coords[0]} Y{start_coords[1]} F6000"
            self.send_gcode(gcode_start)

            # Activate electromagnet to pick up the piece
            self.electromagnet.activate()
            time.sleep(1)  # Short delay to ensure piece is magnetized
            
            #Go in the corner
            gcode_corner = f"G1 X{start_coords[0]+25} Y{start_coords[1]+25} F6000"
            self.send_gcode(gcode_corner)
            time.sleep(1) 

            # First move vertically to the destination row (Y-axis move)
            gcode_vertical_move = f"G1 Y{end_coords[1]-25} F3000"
            self.send_gcode(gcode_vertical_move)
            time.sleep(0.5)  # Delay to ensure the vertical move is complete

            # Then move horizontally to the destination column (X-axis move)
            gcode_horizontal_move = f"G1 X{end_coords[0]-25} F3000"
            self.send_gcode(gcode_horizontal_move)
            time.sleep(0.5)  # Delay to ensure the horizontal move is complete

            gcode_corner = f"G1 X{end_coords[0]+25} Y{end_coords[1]+25} F6000"
            self.send_gcode(gcode_corner)
            time.sleep(1) 
            
            # Deactivate electromagnet to drop the piece
            self.electromagnet.deactivate()
            time.sleep(1)  # Short delay to ensure piece is dropped

        else:
            print("Invalid UCI move or coordinates not found!")

# Example usage
if __name__ == "__main__":
    mainsail_url = "http://your-mainsail-url"  # Replace with your Mainsail URL
    electromagnet_pin = 17  # Example GPIO pin for electromagnet
    chessboard_controller = ChessboardController(mainsail_url, electromagnet_pin)
    
    while True:
        uci_move = input("Enter your move (e.g., e2e4): ")
        chessboard_controller.make_move(uci_move)
