import asyncio
import websockets
import json
import threading  # スレッドを使って非同期に音声を再生
from playsound import playsound
import argparse
import os

# argparseの設定
parser = argparse.ArgumentParser()
parser.add_argument("--address", help="Server address", default="localhost")

# 拡張子を追加する関数
def get_audio_file_with_extension(audio_filename: str) -> str:
    # 音声ファイルのディレクトリ
    audio_dir = "audio"
    # ファイル名に拡張子を追加
    audio_file = f"{audio_filename}.m4a"
    # OSに依存しない形でパスを生成
    return os.path.join(audio_dir, audio_file)

# 音声再生を別スレッドで行う関数
def play_audio_in_thread(audio_file: str):
    try:
        playsound(audio_file)
    except Exception as e:
        print(f"Error playing audio: {e}")

async def handle_audio(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        if 'audio' in data:
            audio_file = get_audio_file_with_extension(data['audio'])
            print(f"Received request to play: {audio_file}")
            # スレッドを使って音声を再生
            threading.Thread(target=play_audio_in_thread, args=(audio_file,), daemon=True).start()

args = parser.parse_args()
address = args.address

# WebSocketサーバーの起動
async def main():
    async with websockets.serve(handle_audio, address, 8080):  # ポート番号を8080に設定
        print("WebSocket server started on ws://"+address+":8080")
        await asyncio.Future()  # サーバーが停止しないようにする

if __name__ == "__main__":
    asyncio.run(main())
