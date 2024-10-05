import numpy as np
from classes.pose import Pose

def assign_poses_to_people(people, poses):
    """
    人物とポーズの紐付けを行う関数
    people: Personオブジェクトのリスト
    poses: ポーズ情報のリスト
    """
    assigned_poses = []  # 既に紐付けられたposeを管理

    for person in people:
        person_center = np.array([person.bbox.center()["x"], person.bbox.center()["y"]])
        closest_pose = None
        closest_distance = float('inf')

        for pose_data in poses:
            # Poseオブジェクトの重心を計算
            pose = Pose(pose_data["keypoints"], pose_data["confidence"])
            pose_center = pose.calculate_center()

            if pose_center is None:
                continue

            pose_center_array = np.array([pose_center["x"], pose_center["y"]])  # np.arrayに変換

            # バウンディングボックスの中心との距離を計算
            distance = np.linalg.norm(pose_center_array - person_center)

            # 最も近いポーズを選択
            if distance < closest_distance and pose not in assigned_poses:
                closest_distance = distance
                closest_pose = pose

        # 最も近いポーズをPersonに割り当てる
        if closest_pose:
            person.update_pose(closest_pose)
            assigned_poses.append(closest_pose)

    # 紐付けられなかったポーズは破棄される
