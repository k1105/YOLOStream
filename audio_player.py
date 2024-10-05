import asyncio
import websockets
import json
import threading
import argparse
import os
import pygame  # pygameを使って音量調整と音声再生を行う
from lib.get_audio_file_with_extention import get_audio_file_with_extension
from lib.play_audio_in_thread import play_audio_in_thread

# argparseの設定
parser = argparse.ArgumentParser()
parser.add_argument("--address", help="Server address", default="localhost")

# pygameの初期化
pygame.mixer.init()

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
