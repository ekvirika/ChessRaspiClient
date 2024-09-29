import cv2
import numpy as np

# Initialize a list to store the points
points = []

# Mouse callback function to capture points
def get_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))

# Load the image
image = cv2.imread('chessboard.jpg')
clone = image.copy()

# Create a window and set a mouse callback
cv2.namedWindow('image')
cv2.setMouseCallback('image', get_points)

# Display the image and wait for 4 corner points to be selected
while True:
    cv2.imshow('image', image)
    key = cv2.waitKey(1) & 0xFF

    # Break the loop once 4 points are selected
    if len(points) == 4:
        break

    # If 'r' is pressed, reset the image and points
    if key == ord('r'):
        image = clone.copy()
        points = []

cv2.destroyAllWindows()
