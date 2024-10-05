import pygame

# 音声再生を別スレッドで行う関数（音量調整を含む）
def play_audio_in_thread(audio_file: str, volume: float):
    try:
        # pygame.mixer.Soundを使ってオーディオを重ねて再生
        sound = pygame.mixer.Sound(audio_file)
        sound.set_volume(volume)  # 音量を設定 (0〜1)
        sound.play()  # サウンドを再生（オーバーラップ再生可能）
    except Exception as e:
        print(f"Error playing audio: {e}")