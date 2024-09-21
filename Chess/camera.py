import cv2
import time

# Open the webcam (0 for default, change if needed)
cap = cv2.VideoCapture(1)

# Set up frame rate for 2 frames per second
frame_rate = 2
prev = 0

def process_frame(frame):
    # Example preprocessing (convert to grayscale)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Example: Feed it to a chessboard recognition AI model (you need to implement this)
    # chessboard_state = recognize_chessboard(gray_frame)

    # Print or store the recognized state
    print("Processed frame for chessboard recognition")

while True:
    time_elapsed = time.time() - prev
    ret, frame = cap.read()

    if time_elapsed > 1./frame_rate:
        prev = time.time()

        # If frame is read correctly
        if ret:
            # Process the frame
            # (You can save it, display it, or feed it to an AI model)
            cv2.imshow("Camo Stream", frame)
            
            # This is where you will process the frame
            # e.g., pass frame to a chessboard recognition model
            process_frame(frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


# Release the capture and close any OpenCV windows
cap.release()
cv2.destroyAllWindows()
