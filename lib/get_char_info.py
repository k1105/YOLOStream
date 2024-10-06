import json
from classes.char_data import CharData

# 漢数字の対応表
kanji_to_digit = {
    "一": "1", "二": "2", "三": "3", "四": "4",
    "五": "5", "六": "6", "七": "7", "八": "8",
    "九": "9", "十": "10"
}

# カタカナとひらがなの変換マッピング
katakana_to_hiragana = str.maketrans(
    "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン",
    "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
)

# 半角カナとひらがなの変換（例: ﾊ → は）
halfwidth_kana_to_hiragana = str.maketrans(
    "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜｦﾝ",
    "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
)

# 文字の変換関数
def transform_char(char):
    # 1. カタカナ → ひらがな
    char = char.translate(katakana_to_hiragana)
    
    # 2. 半角カナ → ひらがな
    char = char.translate(halfwidth_kana_to_hiragana)
    
    # 3. 大文字アルファベット → 小文字アルファベット
    char = char.lower()
    
    # 4. 漢数字 → 算用数字
    char = kanji_to_digit.get(char, char)  # 該当する漢数字があれば変換、なければそのまま
    
    return char

# 変換と検索の例
def get_char_info(char):
    # デフォルトの値を設定
    result = CharData(char, 0, 0, 1, 'none')
    
    # override_char_properties.json を読み込む
    with open('json/override_char_property.json', 'r', encoding='utf-8') as f:
        override_data = json.load(f)
    
    # char でのオーバーライドを確認
    for entry in override_data:
        if entry['char'] == char:
            result.x = entry['x']
            result.y = entry['y']
            result.s = entry['s']
            break  # マッチしたらループを抜ける
    
    # char を変換
    transformed_char = transform_char(char)
    
    # char_audio_index.json を読み込む
    with open('json/char_audio_index.json', 'r', encoding='utf-8') as f:
        audio_data = json.load(f)
    
    # 変換後の char で name を更新
    for entry in audio_data:
        if entry['char'] == transformed_char:
            result.name = entry['name']
            break  # マッチしたらループを抜ける
    
    return result
