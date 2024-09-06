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

    def update_bbox(self, new_bbox: Bbox):
        """
        バウンディングボックスを更新し、速度を計算する
        """
        self.speed = {
            'x': (new_bbox.center()["x"] - self.bbox.center()["x"]) / 2,
            'y': (new_bbox.center()["y"] - self.bbox.center()["y"]) / 2
        }
        self.bbox = new_bbox

    def to_dict(self):
        """
        JSON形式に変換できる辞書形式に変換
        """
        return {
            'id': self.id,
            'speed': self.speed,
            'bbox': self.bbox.to_dict()
        }
