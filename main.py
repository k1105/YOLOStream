import cv2
import json
from ultralytics import YOLO

# Load a pre-trained YOLOv10n model
model = YOLO("yolov10n.pt")

# Initialize the webcam
cap = cv2.VideoCapture(0)  # '0' is usually the default camera, change if necessary

# YOLO推論結果を保存するファイルパス
output_file = "yolo_results.json"

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    # Perform object detection on the current frame
    results = model(frame)

    # Extract the bounding boxes, labels, and confidence scores
    detections = []
    if results[0].boxes is not None:
        for box, score, class_id in zip(results[0].boxes.xyxy, results[0].boxes.conf, results[0].boxes.cls):
            class_id = int(class_id)  # Ensure class_id is an integer
            label = results[0].names[class_id]  # Get the label from the names dictionary
            if label == "person" and score > 0.5:
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
