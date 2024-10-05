class CharData:
    def __init__(self, char, x, y, c, name):
        self.char = char
        self.x = x
        self.y = y
        self.c = c
        self.name = name

    def to_dict(self):
        """
        JSON形式に変換できる辞書形式に変換
        """
        return {
            'char': self.char,
            'x': self.x,
            'y': self.y,
            'c': self.c,
            'name': self.name
        }