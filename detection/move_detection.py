from ultralytics import YOLO
import cv2, numpy as np
import queue


class MD:
    def __init__(self, queue) -> None:
        self.queue = queue

    def get_grid_position(self, x1, y1, x2, y2, square_width, square_height):
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        col = center_x // square_width
        row = center_y // square_height
        return min(max(row, 0), self.GRID_SIZE - 1), min(max(col, 0), self.GRID_SIZE - 1)

    # Function to convert grid positions to UCI notation
    def grid_to_chess_notation(self, row, col):
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
        return files[col] + ranks[row]

    # Function to crop the frame to the desired region
    def crop_frame(self, frame, crop_width, crop_height):
        frame_height, frame_width, _ = frame.shape
        center_x, center_y = frame_width // 2, frame_height // 2
        start_x = center_x - (crop_width // 2)
        start_y = center_y - (crop_height // 2)
        cropped_frame = frame[start_y:start_y + crop_height, start_x:start_x + crop_width]
        return cropped_frame

    # Function to detect differences between two 8x8 grids
    def get_grid_differences(self, grid1, grid2):
        differences = np.argwhere(grid1 != grid2)
        return differences

    def run_move_detection(self):

        # Load your YOLO model for chess piece detection
        model = YOLO('colors.pt')  # Adjust the path to your .pt model

        # Open the camera (Camo Studio)
        cap = cv2.VideoCapture(1)  # Change index if needed for the camera

        # Define chessboard grid size (8x8)
        self.GRID_SIZE = 8

        # Desired crop size (720x720 pixels)
        crop_width = 720
        crop_height = 720

        # Previous grid to detect moves
        previous_grid = None

        # Function to convert detection coordinates to grid position
        while True:
            ret, frame = cap.read()

            if ret:
                # Crop the frame to 720x720 pixels (focused on the chessboard)
                cropped_frame = self.crop_frame(frame, crop_width, crop_height)

                # Perform inference on the cropped frame to detect chess pieces (disable verbose output)
                results = model(cropped_frame, verbose=False)  # Suppress verbose logging

                # Create an 8x8 grid initialized with zeros (no pieces)
                chessboard_grid = np.full((self.GRID_SIZE, self.GRID_SIZE), '0', dtype=str)

                # Calculate square size based on the cropped frame
                square_width = crop_width // self.GRID_SIZE
                square_height = crop_height // self.GRID_SIZE

                # Parse detection results
                detections = results[0].boxes  # Get the detection results

                # Iterate through each detection and fill the grid
                for box in detections:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get box coordinates
                    conf = box.conf[0].item()
                    cls = int(box.cls[0].item())  # Class ID (0 for white, 1 for brown)
                    
                    row, col = self.get_grid_position(x1, y1, x2, y2, square_width, square_height)

                    # Mark this position as occupied by a white (w) or brown (b) piece
                    if cls == 1:  # Assuming class 0 is white
                        chessboard_grid[row, col] = 'w'
                    elif cls == 0:  # Assuming class 1 is brown
                        chessboard_grid[row, col] = 'b'

                    label = f'{model.names[cls]} {conf:.2f}'  # Class label and confidence
                    cv2.rectangle(cropped_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(cropped_frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Display the detections on the screen
                cv2.imshow('Chessboard', cropped_frame)

                # Press 'p' to detect and print the move
                key = cv2.waitKey(1) & 0xFF
                if key == ord('p'):
                    print("8x8 Grid (w = white, b = brown, 0 = empty):")
                    print('\033[94m' + str(chessboard_grid) + '\033[0m')

                    # Compare the current grid with the previous one
                    if previous_grid is not None:
                        differences = self.get_grid_differences(previous_grid, chessboard_grid)
                        
                        # If exactly two squares changed, it's a valid move
                        if len(differences) == 2:
                            row1, col1 = differences[0]
                            row2, col2 = differences[1]
                            mmove = None
                            # Detect the move and convert it to UCI format
                            if previous_grid[row1, col1] != '0' and chessboard_grid[row2, col2] != '0':
                                start_position = self.grid_to_chess_notation(row1, col1)
                                end_position = self.grid_to_chess_notation(row2, col2)
                                mmove = f"{start_position}{end_position}"
                                print(f"\033[92mMove detected: {mmove}\033[0m")
                            elif previous_grid[row2, col2] != '0' and chessboard_grid[row1, col1] != '0':
                                start_position = self.grid_to_chess_notation(row1, col1)
                                end_position = self.grid_to_chess_notation(row2, col2)
                                mmove = f"{end_position}{start_position}"
                                print(f"\033[92mMove detected: {mmove} \033[0m")
                            
                            self.queue.put(mmove)
                            # Print the move in UCI format
                        elif len(differences) == 4 :
                            row1, col1 = differences[0]
                            row2, col2 = differences[1]
                            row3, col3 = differences[2]
                            row4, col4 = differences[3]
                            print(differences)
                            if self.grid_to_chess_notation(row2, col2) == 'c8' and self.grid_to_chess_notation(row3, col3) == 'd8':
                                move = 'e8c8'
                                self.queue.put(move)
                            elif self.grid_to_chess_notation(row2, col2) == 'f8' and self.grid_to_chess_notation(row3, col3) == 'g8':
                                move = 'e8g8'
                                self.queue.put(move)

                    # Save the current grid as the previous grid for future comparison
                    previous_grid = chessboard_grid.copy()

                # Press 'ESC' to exit
                if key == 27:
                    break

        # Release the camera and close all windows
        cap.release()
        cv2.destroyAllWindows()
