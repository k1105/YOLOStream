import time
from classes.bbox import Bbox
from classes.char_data import CharData
import random

class Person:
    def __init__(self, id, speed, bbox: Bbox, displayCharacter: CharData, movingStatus="paused"):
        """
        id: 人物を一意に識別するID
        speed: {'x': x方向の速度, 'y': y方向の速度} 形式の速度
        bbox: Bboxオブジェクト（人物のバウンディングボックス）
        displayCharacter: CharDataオブジェクト（表示する文字）
        movingStatus: 人物の移動状態（デフォルトは "paused"）
        """
        self.id = id
        self.speed = speed
        self.bbox = bbox
        self.lostFrameCount = 0
        self.last_update_time = time.time()  # 最後に更新された時間を保存
        self.unit_time = 1.0 
        self.displayCharacter = displayCharacter
        self.movingStatus = movingStatus
        self.pausedFrameCount = 0  # 停止状態のフレームカウントを初期化
        self.charIndex = None  # 前回のインデックスを保存する
        self.characterUpdated = False

    def update_bbox(self, new_bbox: Bbox):
        current_time = time.time()
        time_diff = current_time - self.last_update_time  # 前回の更新からの時間差

        if time_diff > 0:
            scale_factor = self.unit_time / time_diff  # 時間差をフレーム時間にスケーリング
            self.speed['x'] = (new_bbox.center()["x"] - self.bbox.center()["x"]) * scale_factor
            self.speed['y'] = (new_bbox.center()["y"] - self.bbox.center()["y"]) * scale_factor

        self.bbox = new_bbox
        self.last_update_time = current_time  # 更新時間を記録

    def update_moving_status(self, x_speed_threshold: float, y_speed_threshold: float):
        """
        移動状態を更新するメソッド
        x_speed_threshold: x方向の速度の閾値
        y_speed_threshold: y方向の速度の閾値
        """
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
            self.pausedFrameCount = 0  # 動いている場合はカウントをリセット

    def update_display_character(self, character_data):
        """
        バウンディングボックスの大きさと移動状態から最適な文字を探し、displayCharacterとcharIndexを更新するメソッド
        """
        width = self.bbox.size()["width"]
        height = self.bbox.size()["height"]
        aspect_ratio = width / height
        closest_index = 0
        min_difference = float('inf')

        # 最も近いアスペクト比を探す
        for index, data in enumerate(character_data):
            diff = abs(aspect_ratio - data['aspect-ratio'])
            if diff < min_difference:
                min_difference = diff
                closest_index = index

        # movingStatus に基づいて適切な文字リストを選択
        selected_characters = (
            character_data[closest_index]['walking']
            if self.movingStatus == "walking"
            else character_data[closest_index]['paused']
        )

        # 前回と異なるインデックスなら新しい文字を選ぶ
        if closest_index != self.charIndex and len(selected_characters) > 0:
            if len(selected_characters) == 1:
                c = selected_characters[0]
            else:
                c = random.choice(selected_characters)

            if c['char'] != self.displayCharacter.char:
                self.characterUpdated = True 
            self.displayCharacter = CharData(c['char'], c['x'], c['y'], c['s'], c['name'])

        # インデックスを更新
        self.charIndex = closest_index

    def to_dict(self):
        """
        JSON形式に変換できる辞書形式に変換
        """
        return {
            'id': self.id,
            'speed': self.speed,
            'bbox': self.bbox.to_dict(),
            'displayCharacter': self.displayCharacter.to_dict(),
            'movingStatus': self.movingStatus
        }
