
import time, socket, queue, threading
import math
import requests  # To send HTTP requests to Mainsail
from Board import Board  # Assuming you have the Board class defined in a file named board.py
from Electromagnet import Electromagnet  # Assuming Electromagnet class is defined similarly
import RPi.GPIO as GPIO

class ChessboardController:
    def __init__(self, mainsail_url, electromagnet_pin, default_feed_rate=6000, queue):
        self.board = Board()
        self.mainsail_url = mainsail_url
        self.default_feed_rate = default_feed_rate  # mm/min
        GPIO.cleanup()
        self.electromagnet = Electromagnet(electromagnet_pin)
        self.last_move = [self.board.start_x-25, self.board.start_y]
        self.capture_area = [405, 0]
        self.isWhiteMoved = False
        self.isBlackMoved = False
        self.queue = queue


    def handle_capture(self, captured_square):
        """Move the captured piece to the capture area in a controlled manner."""
        # Get Klipper coordinates for the captured piece
        captured_coords = self.board.get_klipper_coords(captured_square)
        
        # Extract file (column) and rank (row) from the captured square
        captured_file = captured_square[0]  # E.g., 'a' from 'a1'
        captured_rank = int(captured_square[1])  # E.g., 1 from 'a1'

        # Determine X coordinate based on rank
        if captured_rank <= 4:
            x_target = 0
        else:
            x_target = 410

        # Determine Y movement direction based on file
        if captured_file <= 'd':
            y_offset = -25
        else:
            y_offset = 25

        # Move to the captured piece's position
        gcode_move_to_captured = f"G1 X{captured_coords[0]} Y{captured_coords[1]} F{self.default_feed_rate}"
        self.send_gcode(gcode_move_to_captured)
        
        # Activate electromagnet to pick up the captured piece
        time.sleep(self.calculate_delay(self.last_move, captured_coords, self.default_feed_rate))
        self.electromagnet.activate()
        
        # Step 1: Move Y by the calculated offset (Y +/- 25)
        gcode_move_y_offset = f"G1 Y{captured_coords[1] + y_offset} F{self.default_feed_rate}"
        self.send_gcode(gcode_move_y_offset)
        time.sleep(self.calculate_delay(captured_coords, [captured_coords[0], captured_coords[1] + y_offset], self.default_feed_rate))

        # Step 2: Move to the X coordinate based on the rank
        gcode_move_to_x_target = f"G1 X{x_target} F{self.default_feed_rate}"
        self.send_gcode(gcode_move_to_x_target)
        time.sleep(self.calculate_delay([captured_coords[0], captured_coords[1] + y_offset], [x_target, captured_coords[1] + y_offset], self.default_feed_rate))

        # Deactivate electromagnet to drop the piece
        self.electromagnet.deactivate()
        self.last_move = self.capture_area

    def is_castling_move(self, uci_move):
        """Detects if the UCI move is a castling move."""
        return uci_move in ["e1g1", "e1c1", "e8g8", "e8c8"]
    

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

    def calculate_delay(self, start_coords, end_coords, speed):
        """Calculate the delay time based on the distance and feed rate."""
        # Calculate Euclidean distance between two points
        distance = math.sqrt((end_coords[0] - start_coords[0]) ** 2 + (end_coords[1] - start_coords[1]) ** 2)
        
        # Convert feed rate from mm/min to mm/sec
        feed_rate_mm_sec = speed / 60.0
        
        # Calculate time to travel the distance
        time_to_move = distance / feed_rate_mm_sec
        return time_to_move  + 0.5

    def is_knight_move(self, start_square, end_square):
        """Detects if the move is a knight move based on chess logic."""
        start_file = ord(start_square[0])  # Convert letter to ASCII value
        start_rank = int(start_square[1])
        end_file = ord(end_square[0])
        end_rank = int(end_square[1])

        file_diff = abs(start_file - end_file)
        rank_diff = abs(start_rank - end_rank)

        return (file_diff == 2 and rank_diff == 1) or (file_diff == 1 and rank_diff == 2)

    def handle_castling(self, king_move):
        # Determine the corresponding rook's move based on the king's move
        if king_move == "e1g1":  # White kingside castling
            rook_move = "h1f1"
        elif king_move == "e1c1":  # White queenside castling
            rook_move = "a1d1"
        elif king_move == "e8g8":  # Black kingside castling
            rook_move = "h8f8"
        elif king_move == "e8c8":  # Black queenside castling
            rook_move = "a8d8"
        else:
            print("Invalid castling move!")
            return

        # Move the king first
        self.castle_move(king_move)

        # Now handle the rook's move
        rook_start = rook_move[:2]
        rook_end = rook_move[2:]
        
        rook_start_coords = self.board.get_klipper_coords(rook_start)
        rook_end_coords = self.board.get_klipper_coords(rook_end)
        
        if rook_start_coords and rook_end_coords:
            # Move to rook's start square
            gcode_rook_start = f"G1 X{rook_start_coords[0]} Y{rook_start_coords[1]} F{self.default_feed_rate}"
            self.send_gcode(gcode_rook_start)
            time.sleep(self.calculate_delay(self.last_move, rook_start_coords, self.default_feed_rate))
            self.electromagnet.activate()

            if rook_start[1] == '1' :

                # Move rook via edges of the board (e.g., X-axis first, then Y-axis)
                gcode_rook_to_edge = f"G1 X{rook_start_coords[0]-30} Y{rook_start_coords[1]} F{self.default_feed_rate}"
                self.send_gcode(gcode_rook_to_edge)
                time.sleep(self.calculate_delay(rook_start_coords, [rook_start_coords[0]-30, rook_start_coords[1]], self.default_feed_rate))


                gcode_rook_to_end = f"G1 X{rook_end_coords[0]-30} Y{rook_end_coords[1]} F{self.default_feed_rate}"
                self.send_gcode(gcode_rook_to_end)
                time.sleep(self.calculate_delay([rook_start_coords[0]-30, rook_start_coords[1]], [rook_end_coords[0]-30, rook_end_coords[1]], self.default_feed_rate))


                # Move to destination
                gcode_rook_to_end = f"G1 X{rook_end_coords[0]} Y{rook_end_coords[1]} F{self.default_feed_rate}"
                self.send_gcode(gcode_rook_to_end)
                time.sleep(self.calculate_delay([rook_end_coords[0]-30, rook_end_coords[1]], rook_end_coords, self.default_feed_rate))

                # Drop the rook
                self.electromagnet.deactivate()
                self.last_move = rook_end_coords

            else:

                # Move rook via edges of the board (e.g., X-axis first, then Y-axis)
                gcode_rook_to_edge = f"G1 X{rook_start_coords[0]+27} Y{rook_start_coords[1]} F{self.default_feed_rate}"
                self.send_gcode(gcode_rook_to_edge)
                time.sleep(self.calculate_delay(rook_start_coords, [rook_start_coords[0]+27, rook_start_coords[1]], self.default_feed_rate))


                gcode_rook_to_end = f"G1 X{rook_end_coords[0]+27} Y{rook_end_coords[1]} F{self.default_feed_rate}"
                self.send_gcode(gcode_rook_to_end)
                time.sleep(self.calculate_delay([rook_start_coords[0]+27, rook_start_coords[1]], [rook_end_coords[0]+27, rook_end_coords[1]], self.default_feed_rate))


                # Move to destination
                gcode_rook_to_end = f"G1 X{rook_end_coords[0]} Y{rook_end_coords[1]} F{self.default_feed_rate}"
                self.send_gcode(gcode_rook_to_end)
                time.sleep(self.calculate_delay([rook_end_coords[0]+27, rook_end_coords[1]], rook_end_coords, self.default_feed_rate))

                # Drop the rook
                self.electromagnet.deactivate()
                self.last_move = rook_end_coords
        else:
            print("Invalid rook move or coordinates not found!")        
        

    
    def castle_move(self, king_move):
        """Move the king as part of the castling procedure."""
        # Extract king's start and end positions from the UCI move
        king_start = king_move[:2]
        if king_start ==  'd1':
            self.isWhiteMoved = True
        if king_start ==  'e8':
            self.isBlackMoved = True
        king_end = king_move[2:]

        # Get the Klipper coordinates for the king's start and end positions
        king_start_coords = self.board.get_klipper_coords(king_start)
        king_end_coords = self.board.get_klipper_coords(king_end)

        if king_start_coords and king_end_coords:
            # Move to the king's start square
            gcode_king_start = f"G1 X{king_start_coords[0]} Y{king_start_coords[1]} F{self.default_feed_rate}"
            self.send_gcode(gcode_king_start)
            time.sleep(self.calculate_delay(self.last_move, king_start_coords, self.default_feed_rate))

            # Activate the electromagnet to pick up the king
            self.electromagnet.activate()
            print("Electromagnet activated to pick up the king.")

            # Move the king to its destination square
            gcode_king_end = f"G1 X{king_end_coords[0]} Y{king_end_coords[1]} F{self.default_feed_rate}"
            self.send_gcode(gcode_king_end)
            time.sleep(self.calculate_delay(king_start_coords, king_end_coords, self.default_feed_rate))

            # Deactivate the electromagnet to place the king at the destination
            self.electromagnet.deactivate()
            print("Electromagnet deactivated to place the king.")

            # Update the last move coordinates to the king's final position
            self.last_move = king_end_coords
        else:
            print("Invalid king move or coordinates not found!")


    def make_move(self, uci_move, isCapture):
        """Executes a move on the physical chessboard with additional logic for captures and castling."""
        if self.is_castling_move(uci_move):
            # Handle castling move
            print(f"Handling castling: {uci_move}")
            self.handle_castling(uci_move)
            return  # Ensure no further logic is executed for castling
        
        start_square = uci_move[:2]
        end_square = uci_move[2:]
        if start_square == 'e1' and not self.is_castling_move(uci_move):
            self.isWhiteMoved = True
        if start_square == 'e8' and not self.is_castling_move(uci_move):
            self.isBlackMoved = True

        # Get Klipper coordinates for the start and end squares
        start_coords = self.board.get_klipper_coords(start_square)
        end_coords = self.board.get_klipper_coords(end_square)

        if start_coords and end_coords:
            # Move to the start square
            gcode_start = f"G1 X{start_coords[0]} Y{start_coords[1]} F{self.default_feed_rate}"
            self.send_gcode(gcode_start)

            # Calculate appropriate delay
            delay = self.calculate_delay(self.last_move, start_coords, 10000)
            time.sleep(delay)  # Short delay to ensure piece is magnetized
            self.electromagnet.activate()
            if self.is_knight_move(start_square, end_square):
                print("Knight move detected, using existing logic.")
                # Move to corner
                gcode_corner = f"G1 X{start_coords[0]+25} Y{start_coords[1]-25} F{self.default_feed_rate}"
                self.send_gcode(gcode_corner)

                delay = self.calculate_delay(start_coords, [start_coords[0]+25, start_coords[1]-25], self.default_feed_rate)
                time.sleep(delay)

                # Move to destination
                gcode_vertical_move = f"G1 Y{end_coords[1]-25} F{self.default_feed_rate}"
                self.send_gcode(gcode_vertical_move)

                delay = self.calculate_delay([start_coords[0]+25, start_coords[1]-25], [start_coords[0]+25, end_coords[1]-25], self.default_feed_rate)
                time.sleep(delay)

                gcode_horizontal_move = f"G1 X{end_coords[0]-25} F{self.default_feed_rate}"
                self.send_gcode(gcode_horizontal_move)

                delay = self.calculate_delay([start_coords[0]+25, end_coords[1]-25], [end_coords[0]-25, end_coords[1]-25], self.default_feed_rate)
                time.sleep(delay)

                gcode_corner = f"G1 X{end_coords[0]} Y{end_coords[1]} F{self.default_feed_rate}"
                self.send_gcode(gcode_corner)

                delay = self.calculate_delay([end_coords[0]-25, end_coords[1]-25], end_coords, self.default_feed_rate)
                time.sleep(delay)

            else:
                # Check if it's a diagonal move
                if abs(ord(start_square[0]) - ord(end_square[0])) == abs(int(start_square[1]) - int(end_square[1])):
                    print("Diagonal move detected, moving in a single step.")
                    # Diagonal move (X and Y move together)
                    gcode_diag_move = f"G1 X{end_coords[0]} Y{end_coords[1]} F{self.default_feed_rate}"
                    self.send_gcode(gcode_diag_move)

                    delay = self.calculate_delay(start_coords, end_coords,self.default_feed_rate)
                    time.sleep(delay)

                else:
                    # Straight move: either rank or file is the same
                    print("Straight move detected.")
                    if start_coords[0] == end_coords[0]:
                        # Same column, move along Y-axis only
                        gcode_vertical_move = f"G1 Y{end_coords[1]} F{self.default_feed_rate}"
                        self.send_gcode(gcode_vertical_move)

                        delay = self.calculate_delay(start_coords, end_coords, self.default_feed_rate)
                        time.sleep(delay)

                    elif start_coords[1] == end_coords[1]:
                        # Same row, move along X-axis only
                        gcode_horizontal_move = f"G1 X{end_coords[0]} F{self.default_feed_rate}"
                        self.send_gcode(gcode_horizontal_move)

                        delay = self.calculate_delay(start_coords, end_coords, self.default_feed_rate)
                        time.sleep(delay)
        # Deactivate electromagnet to drop the piece
            self.last_move = end_coords
            time.sleep(3)  # Short delay to ensure piece is dropped
            self.electromagnet.deactivate()


    def make_move(self):
        """Executes a move on the physical chessboard based on UCI move format e.g., 'e2e4'"""
        start_square = uci_move[:2]
        end_square = uci_move[2:]

        # Get the Klipper coordinates for the start and end squares
        start_coords = self.board.get_klipper_coords(start_square)
        end_coords = self.board.get_klipper_coords(end_square)

        if start_coords and end_coords:
            # Move to the start square
            gcode_start = f"G1 X{start_coords[0]} Y{start_coords[1]} F{self.default_feed_rate}"
            self.send_gcode(gcode_start)
            print('57522')
            time.sleep(dela)

            # Activate electromagnet to pick up the piece
            print(self.last_move)
            print(start_coords)
            dela = self.calculate_delay(self.last_move, start_coords, self.default_feed_rate )
            print(dela)
            time.sleep(dela)  # Short delay to ensure piece is magnetized
            self.electromagnet.activate()

            # Check if it's a knight move
            if self.is_knight_move(start_square, end_square):
                print("Knight move detected, using existing logic.")
                # Move to corner
                gcode_corner = f"G1 X{start_coords[0]+25} Y{start_coords[1]-25} F{self.default_feed_rate}"
                self.send_gcode(gcode_corner)

                delay = self.calculate_delay(start_coords, [start_coords[0]+25, start_coords[1]-25], self.default_feed_rate)
                time.sleep(delay)

                # Move to destination
                gcode_vertical_move = f"G1 Y{end_coords[1]-25} F{self.default_feed_rate}"
                self.send_gcode(gcode_vertical_move)

                delay = self.calculate_delay([start_coords[0]+25, start_coords[1]-25], [start_coords[0]+25, end_coords[1]-25], self.default_feed_rate)
                time.sleep(delay)

                gcode_horizontal_move = f"G1 X{end_coords[0]-25} F{self.default_feed_rate}"
                self.send_gcode(gcode_horizontal_move)

                delay = self.calculate_delay([start_coords[0]+25, end_coords[1]-25], [end_coords[0]-25, end_coords[1]-25], self.default_feed_rate)
                time.sleep(delay)

                gcode_corner = f"G1 X{end_coords[0]} Y{end_coords[1]} F{self.default_feed_rate}"
                self.send_gcode(gcode_corner)

                delay = self.calculate_delay([end_coords[0]-25, end_coords[1]-25], end_coords, self.default_feed_rate)
                time.sleep(delay)

            else:
                # Check if it's a diagonal move
                if abs(ord(start_square[0]) - ord(end_square[0])) == abs(int(start_square[1]) - int(end_square[1])):
                    print("Diagonal move detected, moving in a single step.")
                    # Diagonal move (X and Y move together)
                    gcode_diag_move = f"G1 X{end_coords[0]} Y{end_coords[1]} F{self.default_feed_rate}"
                    self.send_gcode(gcode_diag_move)

                    delay = self.calculate_delay(start_coords, end_coords,self.default_feed_rate)
                    time.sleep(delay)

                else:
                    # Straight move: either rank or file is the same
                    print("Straight move detected.")
                    print(start_coords)
                    print(end_coords)
                    if start_coords[0] == end_coords[0]:
                        # Same column, move along Y-axis only
                        gcode_vertical_move = f"G1 Y{end_coords[1]} F{self.default_feed_rate}"
                        self.send_gcode(gcode_vertical_move)
                        
                        delay = self.calculate_delay(start_coords, end_coords, self.default_feed_rate)
                        time.sleep(delay)

                    elif start_coords[1] == end_coords[1]:
                        # Same row, move along X-axis only
                        gcode_horizontal_move = f"G1 X{end_coords[0]} F{self.default_feed_rate}"
                        self.send_gcode(gcode_horizontal_move)
                        print('1')

                        delay = self.calculate_delay(start_coords, end_coords, self.default_feed_rate)
                        time.sleep(delay)
            # Deactivate electromagnet to drop the piece
            self.last_move = end_coords
            time.sleep(3)  # Short delay to ensure piece is dropped
            self.electromagnet.deactivate()
        else:
            print("Invalid UCI move or coordinates not found!")

    



if __name__ == "__main__":
    mainsail_url = "http://127.0.0.1:7125"  # Replace with your Mainsail URL
    electromagnet_pin = 11  # Example GPIO pin for electromagnet
    chessboard_controller = ChessboardController(mainsail_url, electromagnet_pin)\


