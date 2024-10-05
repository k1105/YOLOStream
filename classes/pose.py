class Pose:
    def __init__(self, keypoints, confidence):
        """
        keypoints: キーポイントのリスト (各キーポイントは [x, y] の形式)
        confidence: 各キーポイントに対応する信頼度のリスト
        """
        self.keypoints = keypoints
        self.confidence = confidence

    def to_dict(self):
        """
        Pose情報を辞書形式に変換するメソッド
        """
        return {
            "keypoints": self.keypoints,
            "confidence": self.confidence
        }

    def calculate_center(self):
        """
        キーポイントの重心を計算するメソッド
        """
        if len(self.keypoints) == 0:
            return None

        # keypointsが二重配列になっている前提で処理
        keypoints_array = self.keypoints[0]  # 1人目のキーポイントリストを使用

        x_coords = [kp[0] for kp in keypoints_array]
        y_coords = [kp[1] for kp in keypoints_array]

        return {
            "x": sum(x_coords) / len(x_coords),
            "y": sum(y_coords) / len(y_coords)
        }

