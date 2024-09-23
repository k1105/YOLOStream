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
    
    def size(self):
        """バウンディングボックスの幅と高さを計算する"""
        return {
            'width': self.bbox[2] - self.bbox[0],
            'height': self.bbox[3] - self.bbox[1]
        }

    def is_similar(self, other_bbox, center_threshold=100, size_threshold=100):
        """
        2つのバウンディングボックスが近いかを判定
        center_threshold: 中心座標の差の許容値
        size_threshold: サイズの差の許容割合
        """
        # 中心座標の比較
        center_self = self.center()
        center_other = other_bbox.center()
        center_diff = ((center_self['x'] - center_other['x']) ** 2 +
                       (center_self['y'] - center_other['y']) ** 2) ** 0.5

        # サイズの比較
        size_self = self.size()
        size_other = other_bbox.size()
        width_diff = abs(size_self['width'] - size_other['width']) / size_self['width']
        height_diff = abs(size_self['height'] - size_other['height']) / size_self['height']

        # 中心が近く、サイズの差が許容範囲内か
        return center_diff < center_threshold and width_diff < size_threshold and height_diff < size_threshold

    def to_dict(self):
        """
        JSON形式に変換できる辞書形式に変換
        """
        return {
            'confidence': self.confidence,
            'bbox': self.bbox
        }
