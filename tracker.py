import cv2
import json
import threading
import time
import argparse
from ultralytics import YOLO
from relation_calculator import update_relation
from bbox import Bbox
from person import Person

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
personId = 0
threshold = 200  # 距離の閾値（必要に応じて調整）

output_file = "yolo_results.json"

def update_people(relation, people, bboxes, personId):
    activePersonIds = set([entry['id'] for sublist in relation for entry in sublist])
    people = [person for person in people if person.id in activePersonIds]

    for i in range(len(relation)):
        if len(relation[i]) == 0:
            # 新しい人物がフレームイン
            new_person = Person(personId, {'x': 0, 'y': 0}, bboxes[i])
            people.append(new_person)
            personId += 1
        elif len(relation[i]) == 1:
            # 既存の人物を更新
            person = next((p for p in people if p.id == relation[i][0]['id']), None)
            if person:
                person.update_bbox(bboxes[i])
            else:
                print("更新対象の人物が見つかりません")

    return people, personId

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
    people, personId = update_people(relation, people, bboxes, personId)

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