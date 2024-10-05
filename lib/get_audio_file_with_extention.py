import os

# 拡張子を追加し、ファイルパスを生成する関数
def get_audio_file_with_extension(audio_filename: str) -> str:
    audio_dir = "audio"
    
    try:
        prefix, filename = audio_filename.split("_")
    except ValueError:
        print(f"Invalid audio filename format: {audio_filename}")
        return None

    audio_file = f"{filename}.mp3"  # .mp3 拡張子を使用
    return os.path.join(audio_dir, prefix, audio_file)