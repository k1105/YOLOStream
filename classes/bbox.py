class Bbox:
    def __init__(self, confidence, bbox):
        """
        bbox: [x_min, y_min, x_max, y_max] の形式で指定されたバウンディングボックス
        """
        self.confidence = confidence
        self.bbox = bbox

    def center(self):
        """
        バウンディングボックスの中心点を計算する
        """
        return {
            'x': (self.bbox[0] + self.bbox[2]) / 2,
            'y': (self.bbox[1] + self.bbox[3]) / 2
        }

    def to_dict(self):
        """
        JSON形式に変換できる辞書形式に変換
        """
        return {
            'confidence': self.confidence,
            'bbox': self.bbox
        }
