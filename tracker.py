import cv2
import json
import threading
import argparse
from ultralytics import YOLO
from lib.relation_calculator import update_relation
from classes.bbox import Bbox
from lib.update_people import update_people

# YOLOモデルの読み込み
model = YOLO("yolov10n.pt")

# カメラの初期化
cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"カメラの解像度: {width}x{height}")

parser = argparse.ArgumentParser()
parser.add_argument("--mirrored", help="optional", action="store_true")

people = []
bboxes = []
peopleCounts = 0
threshold = 200  # 距離の閾値（必要に応じて調整）
bbox_buffer = {}
bufferedBboxCount = 0  # バッファのBboxに一意なIDを付与するカウンター

output_file = "yolo_results.json"

# YOLOの推論を別スレッドで実行
def yolo_detection(frame, results_container):
    arg = parser.parse_args()
    if arg.mirrored:
        frame = cv2.flip(frame, 1)
    results = model(frame)
    results_container['results'] = results

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLOによる人物検出のスレッドを作成
    results_container = {}
    yolo_thread = threading.Thread(target=yolo_detection, args=(frame, results_container))
    yolo_thread.start()

    # YOLOの推論が終わるまでの間に他の処理を行う
    relation = update_relation(people, bboxes, threshold)  # bboxesが空でも処理する
    people, peopleCounts, bbox_buffer, bufferedBboxCount = update_people(relation, people, bboxes, bbox_buffer, peopleCounts, bufferedBboxCount)
    # people, peopleCounts = update_people(relation, people, bboxes, peopleCounts)

    # YOLOの推論が終わるまで待機
    yolo_thread.join()

    # YOLOの結果を処理
    results = results_container.get('results')
    if results and results[0].boxes is not None:
        bboxes = [Bbox(float(score), [float(b) for b in box.numpy()])
                  for box, score, class_id in zip(results[0].boxes.xyxy, results[0].boxes.conf, results[0].boxes.cls)
                  if int(class_id) == 0 and score > 0.5]  # bboxesを更新
    else:
        bboxes = []  # 人が検出されない場合はbboxesを空にする

    # JSONファイルへの書き込み
    json_data = [person.to_dict() for person in people]

    with open(output_file, "w") as f:
        json.dump(json_data, f)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()