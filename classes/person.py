import time
from classes.bbox import Bbox
from classes.char_data import CharData

class Person:
    def __init__(self, id, speed, bbox: Bbox, displayCharacter: CharData, movingStatus):
        """
        id: 人物を一意に識別するID
        speed: {'x': x方向の速度, 'y': y方向の速度} 形式の速度
        bbox: Bboxオブジェクト（人物のバウンディングボックス）
        fps: システムのフレームレート（デフォルトは60）
        smoothing_factor: 平滑化係数（0~1の範囲、1に近いほど現在の値を重視）
        """
        self.id = id
        self.speed = speed
        self.bbox = bbox
        self.lostFrameCount = 0
        self.last_update_time = time.time()  # 最後に更新された時間を保存
        self.unit_time = 1.0 
        self.displayCharacter = displayCharacter
        self.movingStatus = movingStatus
        
    def update_bbox(self, new_bbox: Bbox):
        current_time = time.time()
        time_diff = current_time - self.last_update_time  # 前回の更新からの時間差

        if time_diff > 0:
            scale_factor = self.unit_time / time_diff  # 時間差をフレーム時間にスケーリング
            self.speed['x'] = (new_bbox.center()["x"] - self.bbox.center()["x"]) * scale_factor
            self.speed['y'] = (new_bbox.center()["y"] - self.bbox.center()["y"]) * scale_factor

        self.bbox = new_bbox
        self.last_update_time = current_time  # 更新時間を記録

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
