from classes.bbox import Bbox
from classes.char_data import CharData
import random
import time
from classes.pose import Pose

class Person:
    def __init__(self, id, speed, bbox: Bbox, displayCharacter: CharData, movingStatus="paused", pose=None):
        self.id = id
        self.speed = speed
        self.bbox = bbox
        self.pose = pose  # Poseオブジェクトを持つ
        self.lostFrameCount = 0
        self.last_update_time = time.time()
        self.unit_time = 1.0
        self.displayCharacter = displayCharacter
        self.movingStatus = movingStatus
        self.pausedFrameCount = 0
        self.charIndex = None
        self.characterUpdated = False

    def update_bbox(self, new_bbox: Bbox):
        current_time = time.time()
        time_diff = current_time - self.last_update_time

        if time_diff > 0:
            scale_factor = self.unit_time / time_diff
            self.speed['x'] = (new_bbox.center()["x"] - self.bbox.center()["x"]) * scale_factor
            self.speed['y'] = (new_bbox.center()["y"] - self.bbox.center()["y"]) * scale_factor

        self.bbox = new_bbox
        self.last_update_time = current_time

    def update_moving_status(self, x_speed_threshold: float, y_speed_threshold: float):
        speed = self.speed
        if (
            (abs(speed['x']) > x_speed_threshold and abs(speed['x'] / speed['y']) > 2) or 
            self.movingStatus == "walking"
        ):
            self.movingStatus = "walking"

        if abs(speed['x']) < x_speed_threshold and abs(speed['y']) < y_speed_threshold:
            self.pausedFrameCount += 1
            if self.pausedFrameCount > 3:
                self.movingStatus = "paused"
        else:
            self.pausedFrameCount = 0

    def update_display_character(self, character_data):
        width = self.bbox.size()["width"]
        height = self.bbox.size()["height"]
        aspect_ratio = width / height
        closest_index = 0
        min_difference = float('inf')

        for index, data in enumerate(character_data):
            diff = abs(aspect_ratio - data['aspect-ratio'])
            if diff < min_difference:
                min_difference = diff
                closest_index = index

        selected_characters = (
            character_data[closest_index]['walking']
            if self.movingStatus == "walking"
            else character_data[closest_index]['paused']
        )

        if closest_index != self.charIndex and len(selected_characters) > 0:
            if len(selected_characters) == 1:
                c = selected_characters[0]
            else:
                c = random.choice(selected_characters)

            if c['char'] != self.displayCharacter.char:
                self.characterUpdated = True 
            self.displayCharacter = CharData(c['char'], c['x'], c['y'], c['s'], c['name'])

        self.charIndex = closest_index

    def update_pose(self, pose: Pose):
        """
        Poseオブジェクトを更新
        """
        self.pose = pose

    def to_dict(self):
        """
        JSON形式に変換できる辞書形式に変換
        """
        return {
            'id': self.id,
            'speed': self.speed,
            'bbox': self.bbox.to_dict(),
            'displayCharacter': self.displayCharacter.to_dict(),
            'movingStatus': self.movingStatus,
            'pose': self.pose.to_dict() if self.pose else None  # Poseデータを追加
        }
