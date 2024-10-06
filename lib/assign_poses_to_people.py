import numpy as np
from classes.pose import Pose

def assign_poses_to_people(people, poses):
    assigned_pose_centers = []  # 既に紐付けられたposeを管理

    for person in people:
        person_center = np.array([person.bbox.center()["x"], person.bbox.center()["y"]])
        closest_pose = None
        closest_distance = float('inf')
        closest_pose_center = None

        # keypoints の構造に基づき、正しくアクセス
        if len(poses) > 0:
            for person_index in range(len(poses[0]["keypoints"])):
                keypoints = poses[0]["keypoints"][person_index]  # 各人物のキーポイント取得
                confidence = poses[0]["confidence"][person_index]  # 各人物のconfidence取得

                # Pose オブジェクトを作成
                pose = Pose(keypoints, confidence)
                pose_center = pose.calculate_center()

                if pose_center is None:
                    continue

                pose_center_array = np.array([pose_center["x"], pose_center["y"]])  # np.arrayに変換

                if any(np.array_equal(pose_center_array, assigned_pose) for assigned_pose in assigned_pose_centers):
                    continue

                # バウンディングボックスの中心との距離を計算
                distance = np.linalg.norm(pose_center_array - person_center)

                # 最も近いポーズを選択
                if distance < closest_distance:
                    closest_distance = distance
                    closest_pose = pose
                    closest_pose_center = pose_center_array

        # 最も近いポーズをPersonに割り当てる
        if closest_pose:
            person.update_pose(closest_pose)
            assigned_pose_centers.append(closest_pose_center)

    # 紐付けられなかったポーズは破棄される
