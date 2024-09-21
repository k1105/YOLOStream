import time
from bbox import Bbox

class Person:
    def __init__(self, id, speed, bbox: Bbox):
        """
        id: 人物を一意に識別するID
        speed: {'x': x方向の速度, 'y': y方向の速度} 形式の速度
        bbox: Bboxオブジェクト（人物のバウンディングボックス）
        """
        self.id = id
        self.speed = speed
        self.bbox = bbox
        self.lostFrameCount = 0
        self.last_update_time = time.time()  # 最後に更新された時間を保存

    def update_bbox(self, new_bbox: Bbox):
        """
        バウンディングボックスを更新し、速度を時間差に基づいて計算する
        """
        current_time = time.time()
        time_diff = current_time - self.last_update_time  # 前の更新からの時間差を計算

        if time_diff > 0:  # 0除算を避ける
            self.speed = {
                'x': (new_bbox.center()["x"] - self.bbox.center()["x"]) / time_diff,
                'y': (new_bbox.center()["y"] - self.bbox.center()["y"]) / time_diff
            }

        self.bbox = new_bbox
        self.last_update_time = current_time  # 更新時間を記録

    def to_dict(self):
        """
        JSON形式に変換できる辞書形式に変換
        """
        return {
            'id': self.id,
            'speed': self.speed,
            'bbox': self.bbox.to_dict()
        }
