import cv2
from ultralytics import YOLO

# Load your YOLOv8 model
model = YOLO('best.pt')  # Adjust the path to your .pt model

# Open the Camo virtual camera (usually at index 0)
cap = cv2.VideoCapture(1)

frame_path = 'detected_frame.jpg'  # File path to save the frame

while True:
    ret, frame = cap.read()

    if ret:
        # Perform inference on the frame
        results = model(frame)

        # Parse results
        detections = results[0].boxes  # Get the detection results

        # Draw bounding boxes and labels on the frame
        for box in detections:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Get box coordinates
            conf = box.conf[0].item()  # Confidence score
            cls = int(box.cls[0].item())  # Class index
            label = f'{model.names[cls]} {conf:.2f}'  # Class label and confidence
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Save the processed frame
        cv2.imwrite(frame_path, frame)

        # Optional: print the path where the frame is saved
        print(f"Saved frame to {frame_path}")

        # Break the loop if 'q' is pressed
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

# Release the capture and close any OpenCV windows
cap.release()
