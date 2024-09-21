import cv2
import numpy as np
from ultralytics import YOLO

# Load your YOLOv8 model
model = YOLO('best.pt')  # Adjust the path to your .pt model

# Open the Camo virtual camera (usually at index 0)
cap = cv2.VideoCapture(1)

# Define chessboard grid size
GRID_SIZE = 8

# Function to get grid coordinates for a given bounding box center
def get_grid_position(x_center, y_center, frame_width, frame_height):
    # Divide the frame into an 8x8 grid
    grid_x = int((x_center / frame_width) * GRID_SIZE)
    grid_y = int((y_center / frame_height) * GRID_SIZE)
    return grid_x, grid_y

while True:
    ret, frame = cap.read()

    if ret:
        # Resize the frame to a fixed size (e.g., 640x640)
        frame_resized = cv2.resize(frame, (640, 640))
        frame_height, frame_width = frame_resized.shape[:2]

        # Initialize an 8x8 matrix of zeros (no pieces detected)
        chessboard_matrix = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

        # Perform inference on the resized frame
        results = model(frame_resized)

        # Process the detected results
        for box in results[0].boxes:
            # Get the bounding box coordinates and center
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box corners
            x_center = (x1 + x2) // 2
            y_center = (y1 + y2) // 2

            # Map the bounding box center to a grid position
            grid_x, grid_y = get_grid_position(x_center, y_center, frame_width, frame_height)

            # Mark this grid cell as occupied by a piece (1)
            chessboard_matrix[grid_y, grid_x] = 1

        # Print the current 8x8 matrix
        print("Chessboard Matrix:")
        print(chessboard_matrix)

        # Show the original frame with detections (optional)
        cv2.imshow("Original Camo Stream", frame_resized)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture
cap.release()
cv2.destroyAllWindows()
