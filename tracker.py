import cv2
import json
import threading
import argparse
from ultralytics import YOLO
from lib.relation_calculator import update_relation
from classes.bbox import Bbox
from lib.update_people import update_people
import pygame
import threading
import os
from lib.get_audio_file_with_extention import get_audio_file_with_extension
from lib.play_audio_in_thread import play_audio_in_thread

parser = argparse.ArgumentParser()
parser.add_argument("--mirrored", help="optional", action="store_true")
parser.add_argument("--gpu", help="Enable YOLO in gpu mode", action="store_true")
arg = parser.parse_args()

# YOLOモデルの読み込み
bbox_model = YOLO("yolo11n.pt").gpu() if arg.gpu else YOLO("yolo11n.pt")
pose_model = YOLO("yolo11n-pose.pt").gpu() if arg.gpu else YOLO("yolo11n-pose.pt")

# カメラの初期化
cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"カメラの解像度: {width}x{height}")

people = []
bboxes = []
peopleCounts = 0
threshold = 200
bbox_buffer = {}
bufferedBboxCount = 0

people_output_file = "people_results.json"
pose_output_file = "pose_results.json"

# pygameの初期化
pygame.mixer.init()

# YOLOの推論を別スレッドで実行
def yolo_detection(frame, results_container):
    if arg.mirrored:
        frame = cv2.flip(frame, 1)
    # 物体検出モデルで推論
    bbox_results = bbox_model(frame)
    # ポーズ推定モデルで推論
    pose_results = pose_model(frame)
    
    results_container['bbox_results'] = bbox_results
    results_container['pose_results'] = pose_results

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results_container = {}
    yolo_thread = threading.Thread(target=yolo_detection, args=(frame, results_container))
    yolo_thread.start()

    relation = update_relation(people, bboxes, threshold)
    people, peopleCounts, bbox_buffer, bufferedBboxCount = update_people(relation, people, bboxes, bbox_buffer, peopleCounts, bufferedBboxCount)
    
    for person in people:
        if person.characterUpdated:
            audio_file = get_audio_file_with_extension(person.displayCharacter.name)
            volume = 1  # 音量設定
            if audio_file and os.path.exists(audio_file):
                print(f"Playing audio: {audio_file} at volume: {volume}")
                threading.Thread(target=play_audio_in_thread, args=(audio_file, volume), daemon=True).start()
            else:
                print(f"Audio file not found: {audio_file}")
            person.characterUpdated = False

    yolo_thread.join()

    # YOLOの結果を処理
    bbox_results = results_container.get('bbox_results')
    pose_results = results_container.get('pose_results')
    
    if bbox_results and bbox_results[0].boxes is not None:
        bboxes = [Bbox(float(score), [float(b) for b in box.numpy()])
                  for box, score, class_id in zip(bbox_results[0].boxes.xyxy, bbox_results[0].boxes.conf, bbox_results[0].boxes.cls)
                  if int(class_id) == 0 and score > 0.5]
    else:
        bboxes = []

    # ポーズ推定結果を pose 配列に保持
    if pose_results:
        pose_data = []
        for person_pose in pose_results:
            if person_pose.keypoints is not None:
                if person_pose.keypoints.xy is not None and person_pose.keypoints.conf is not None:
                    keypoints_xy = person_pose.keypoints.xy.cpu().numpy().tolist()  # [x, y] 座標を取得
                    keypoints_conf = person_pose.keypoints.conf.cpu().numpy().tolist()  # 信頼度を取得
                    pose_data.append({
                        "keypoints": keypoints_xy,
                        "confidence": keypoints_conf
                    })
                else:
                    print("Keypoints or confidence is None")
                    print(person_pose.keypoints)
            else:
                print("person_pose.keypoints is None")

    # JSONファイルへの書き込み
    people_data = [person.to_dict() for person in people]

    with open(people_output_file, "w") as people_file:
        json.dump(people_data, people_file)

    # JSONファイルへの書き込み (pose_results.json)
    with open(pose_output_file, "w") as pose_file:
        json.dump(pose_data, pose_file)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
