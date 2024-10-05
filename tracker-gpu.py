import cv2
import json
import argparse
from ultralytics import YOLO
from lib.relation_calculator import update_relation
from lib.update_people import update_people

from classes.bbox import Bbox

# argparseの設定
parser = argparse.ArgumentParser()
parser.add_argument("--mirrored", help="optional", action="store_true")
arg = parser.parse_args()

# YOLOモデルの読み込み（GPUを使用）
model = YOLO("yolo11x.pt").to("cuda")

# カメラの初期化
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"カメラの解像度: {width}x{height}")

people = []
bboxes = []
peopleCounts = 0
threshold = 200  # 距離の閾値（必要に応じて調整）
bbox_buffer = {}
bufferedBboxCount = 0  # バッファのBboxに一意なIDを付与するカウンター

output_file = "people_results.json"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # フレームをミラーリングするかを確認
    if arg.mirrored:
        frame = cv2.flip(frame, 1)

    # YOLOによる推論
    results = model(frame)

    # YOLOの結果を処理
    if results and results[0].boxes is not None:
        bboxes = [Bbox(float(score), [float(b) for b in box.cpu().numpy()])
                  for box, score, class_id in zip(results[0].boxes.xyxy, results[0].boxes.conf, results[0].boxes.cls)
                  if int(class_id) == 0 and score > 0.6]
    else:
        bboxes = []  # 人が検出されない場合はbboxesを空にする

    # 人物とバウンディングボックスの関係を更新
    relation = update_relation(people, bboxes, threshold)
    people, peopleCounts, bbox_buffer, bufferedBboxCount = update_people(relation, people, bboxes, bbox_buffer, peopleCounts, bufferedBboxCount)

    # JSONファイルへの書き込み
    json_data = [person.to_dict() for person in people]
    with open(output_file, "w") as f:
        json.dump(json_data, f)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
