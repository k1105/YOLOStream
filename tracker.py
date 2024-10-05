import cv2
import json
import argparse
from ultralytics import YOLO
from lib.relation_calculator import update_relation
from classes.bbox import Bbox
from lib.update_people import update_people
from classes.pose import Pose  # PoseClassをインポート
from lib.assign_poses_to_people import assign_poses_to_people
import pygame
import os
from lib.get_audio_file_with_extention import get_audio_file_with_extension
from lib.play_audio_in_thread import play_audio_in_thread

parser = argparse.ArgumentParser()
parser.add_argument("--mirrored", help="optional", action="store_true")
parser.add_argument("--gpu", help="Enable YOLO in gpu mode", action="store_true")
arg = parser.parse_args()

# YOLOモデルの読み込み
bbox_model = YOLO("yolo11n.pt").to("cuda") if arg.gpu else YOLO("yolo11n.pt")
pose_model = YOLO("yolo11n-pose.pt").to("cuda") if arg.gpu else YOLO("yolo11n-pose.pt")

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

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if arg.mirrored:
        frame = cv2.flip(frame, 1)

    # YOLOによる推論
    bbox_results = bbox_model(frame)
    pose_results = pose_model(frame)

    # YOLOの結果を処理
    if bbox_results and bbox_results[0].boxes is not None:
        bboxes = [Bbox(float(score.cpu()), [float(b) for b in box.cpu().numpy()])
                for box, score, class_id in zip(bbox_results[0].boxes.xyxy, bbox_results[0].boxes.conf, bbox_results[0].boxes.cls)
                if int(class_id) == 0 and score > 0.5]  # GPU -> CPU変換を追加
    else:
        bboxes = []

    # ポーズ推定結果を pose 配列に保持
    pose_data = []
    if pose_results:
        for person_pose in pose_results:
            if person_pose.keypoints is not None and person_pose.keypoints.xy is not None and person_pose.keypoints.conf is not None:
                keypoints_xy = person_pose.keypoints.xy.cpu().numpy().tolist()  # GPU -> CPU変換
                keypoints_conf = person_pose.keypoints.conf.cpu().numpy().tolist()  # GPU -> CPU変換
                pose_data.append({
                    "keypoints": keypoints_xy,
                    "confidence": keypoints_conf
                })

    # 人物とバウンディングボックスの関係を更新
    relation = update_relation(people, bboxes, threshold)
    people, peopleCounts, bbox_buffer, bufferedBboxCount = update_people(relation, people, bboxes, bbox_buffer, peopleCounts, bufferedBboxCount)

    # assign_poses_to_people関数を使用してposeをpeopleに紐付け
    assign_poses_to_people(people, pose_data)

    for person in people:
        if person.characterUpdated:
            audio_file = get_audio_file_with_extension(person.displayCharacter.name)
            volume = 1  # 音量設定
            if audio_file and os.path.exists(audio_file):
                print(f"Playing audio: {audio_file} at volume: {volume}")
                play_audio_in_thread(audio_file, volume)
            else:
                print(f"Audio file not found: {audio_file}")
            person.characterUpdated = False

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
