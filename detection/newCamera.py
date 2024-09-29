# Load your YOLOv8 model
import cv2
import numpy as np
import time
from collections import deque
from ultralytics import YOLO

model = YOLO('bestPieces.pt')  # Adjust the path to your .pt model

# Open the Camo virtual camera (usually at index 1)
cap = cv2.VideoCapture(1)

# Increase camera resolution for better image quality
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Set width for HD or 4K resolution
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # Set height for HD or 4K resolution

frame_path = 'detected_frame.jpg'  # File path to save the frame

# Define the size of the chessboard (8x8 grid)
GRID_SIZE = 8

# Desired crop size (720x720 pixels)
crop_width = 720
crop_height = 720

# Define how many frames to average over (5 frames per second, 1 second for the smoothed matrix)
frame_history_length = 5

# Create a deque to store the recent frame detections
frame_history = deque(maxlen=frame_history_length)

# Store the previous grid state to detect changes
previous_grid = None

# Initialize a timer for the 1-second interval
last_smoothed_time = time.time()

# Mapping of grid positions to chess coordinates
def grid_to_chess_notation(row, col):
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
    return files[col] + ranks[row]

# Function to crop the frame to the desired region
def crop_frame(frame, crop_width, crop_height):
    frame_height, frame_width, _ = frame.shape
    center_x, center_y = frame_width // 2, frame_height // 2
    start_x = center_x - (crop_width // 2)
    start_y = center_y - (crop_height // 2)
    cropped_frame = frame[start_y:start_y + crop_height, start_x:start_x + crop_width]
    return cropped_frame

# Function to convert detection coordinates to a grid position
def get_grid_position(x1, y1, x2, y2, square_width, square_height):
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    col = center_x // square_width
    row = center_y // square_height
    return min(max(row, 0), GRID_SIZE - 1), min(max(col, 0), GRID_SIZE - 1)

# Function to count the differences between two grids and return the changed positions
def get_grid_differences(grid1, grid2):
    differences = np.argwhere(grid1 != grid2)
    return differences

while True:
    ret, frame = cap.read()

    if ret:
        # Crop the frame to 720x720 pixels
        cropped_frame = crop_frame(frame, crop_width, crop_height)

        # Perform inference on the cropped frame
        results = model(cropped_frame)

        # Create an 8x8 grid initialized with zeros (no pieces)
        chessboard_grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

        # Calculate square size based on the cropped frame
        square_width = crop_width // GRID_SIZE
        square_height = crop_height // GRID_SIZE

        # Parse detection results
        detections = results[0].boxes  # Get the detection results

        # Iterate through each detection
        for box in detections:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get box coordinates
            conf = box.conf[0].item()  # Confidence score
            cls = int(box.cls[0].item())  # Class index

            # Get the grid position for this detection
            row, col = get_grid_position(x1, y1, x2, y2, square_width, square_height)

            # Mark this position as occupied by a piece (1 in the grid)
            chessboard_grid[row, col] = 1

            # Draw bounding boxes and labels on the cropped frame
            label = f'{model.names[cls]} {conf:.2f}'  # Class label and confidence
            cv2.rectangle(cropped_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(cropped_frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Add the current frame's grid to the history deque
        frame_history.append(chessboard_grid)

        # Show the current frame in a window
        cv2.imshow('Detected Frame', cropped_frame)

        # Save the processed cropped frame with higher quality
        cv2.imwrite(frame_path, cropped_frame, [cv2.IMWRITE_JPEG_QUALITY, 100])

        # Check if 1 second has passed since the last smoothed matrix
        current_time = time.time()
        if current_time - last_smoothed_time >= 0:
            # Calculate the average grid over the last few frames
            if len(frame_history) == frame_history_length:
                averaged_grid = np.mean(frame_history, axis=0)
                # Apply a threshold to make it binary (either 0 or 1)
                smoothed_grid = (averaged_grid >= 0.5).astype(int)

                # Print the smoothed 8x8 grid (reliable data)
                print("Smoothed 8x8 Grid (1 = piece, 0 = no piece):")
                print(smoothed_grid)

                # Check for changes in chessboard state
                if previous_grid is not None:
                    # Get the differences between the previous and current grid
                    differences = get_grid_differences(previous_grid, smoothed_grid)

                    # If exactly two squares changed, it's a valid move
                    if len(differences) == 2:
                        start_row, start_col = differences[0]
                        end_row, end_col = differences[1]

                        # Determine if a piece moved or a piece was placed/removed
                        if previous_grid[start_row, start_col] == 1 and smoothed_grid[end_row, end_col] == 1:
                            # Valid move detected
                            start_position = grid_to_chess_notation(start_row, start_col)
                            end_position = grid_to_chess_notation(end_row, end_col)
                            move = f"{start_position}{end_position}"

                            # Print the move in UCI format
                            print(f"\033[92mValid move detected {move} \033[0m")

                    # If more than two pieces change, ignore the frame as interference
                    elif len(differences) > 2 or len(differences) == 1:
                        print(f"\033[91mInterference detected, ignoring this frame\033[0m")
                        continue

                # Update the previous grid for the next frame
                previous_grid = smoothed_grid.copy()

            # Update the last smoothed time
            last_smoothed_time = current_time

        # Use time.sleep() to maintain 5 frames per second (200ms pause)
        # time.sleep(0.3)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close any OpenCV windows
cap.release()
cv2.destroyAllWindows()