import asyncio
import websockets
import json
import threading
import argparse
import os
import pygame  # pygameを使って音量調整と音声再生を行う

# argparseの設定
parser = argparse.ArgumentParser()
parser.add_argument("--address", help="Server address", default="localhost")

# pygameの初期化
pygame.mixer.init()

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

# 音声再生を別スレッドで行う関数（音量調整を含む）
def play_audio_in_thread(audio_file: str, volume: float):
    try:
        # pygame.mixer.Soundを使ってオーディオを重ねて再生
        sound = pygame.mixer.Sound(audio_file)
        sound.set_volume(volume)  # 音量を設定 (0〜1)
        sound.play()  # サウンドを再生（オーバーラップ再生可能）
    except Exception as e:
        print(f"Error playing audio: {e}")

async def handle_audio(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        if 'audio' in data and 'volume' in data:
            audio_file = get_audio_file_with_extension(data['audio'])
            volume = data['volume']  # 0〜1の範囲で送られる音量
            if audio_file and os.path.exists(audio_file):
                print(f"Playing audio: {audio_file} at volume: {volume}")
                # スレッドを使って音量付きで音声を再生
                threading.Thread(target=play_audio_in_thread, args=(audio_file, volume), daemon=True).start()
            else:
                print(f"Audio file not found: {audio_file}")

args = parser.parse_args()
address = args.address

# WebSocketサーバーの起動
async def main():
    async with websockets.serve(handle_audio, address, 8080):
        print("WebSocket server started on ws://" + address + ":8080")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
