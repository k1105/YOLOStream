import cv2
import json
from ultralytics import YOLO

# Load a pre-trained YOLOv10n model
model = YOLO("yolov10n.pt")

# Initialize video capture with a video file
video_path = "./video/dotonbori.mov"  # Replace with your video file path
cap = cv2.VideoCapture(video_path)

# YOLO推論結果を保存するファイルパス
output_file = "yolo_results.json"

while True:
    ret, frame = cap.read()
    
    if not ret:
        # If the video ends, loop it
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
    
    # Perform object detection on the current frame
    results = model(frame)

     # Draw the results on the frame
    annotated_frame = results[0].plot()

    # Display the frame
    cv2.imshow("YOLOv10 Real-Time Detection", annotated_frame)

    # Extract the bounding boxes, labels, and confidence scores
    detections = []
    if results[0].boxes is not None:
        for box, score, class_id in zip(results[0].boxes.xyxy, results[0].boxes.conf, results[0].boxes.cls):
            class_id = int(class_id)  # Ensure class_id is an integer
            label = results[0].names[class_id]  # Get the label from the names dictionary
            if label == "person":
                detection = {
                    "confidence": float(score),
                    "bbox": [float(b) for b in box.numpy()]
                }
                detections.append(detection)
    
    # JSON形式でファイルに書き出し
    with open(output_file, "w") as f:
        json.dump(detections, f)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
