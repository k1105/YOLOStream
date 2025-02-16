import asyncio
import websockets
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--address", help="Server address", default="localhost")
args = parser.parse_args()
address = args.address

async def time_server(websocket, path):
    prevData = None
    while True:
        try:
            with open("people_results.json", "r") as file:
                data = json.load(file)
            # ここで「読み込み成功した」ことをログに出す
            print("people_results.json loaded successfully.")
        except FileNotFoundError:
            print("people_results.json not found.")
            data = None
        except json.decoder.JSONDecodeError:
            print("json decode error.")
            data = None

        if data:
            if data != prevData:
                await websocket.send(json.dumps(data))
                print("SENT DATA (people_results.json changed).")
            else:
                # ここで「データが変わっていなかった」ことを示す
                print("people_results.json unchanged; no send.")
        else:
            print("No valid data to send.")

        prevData = data
        await asyncio.sleep(0.01)
        
async def main():
    async with websockets.serve(time_server, address, 8765):
        print(f"WebSocket server started on {address}:8765")
        await asyncio.Future()  # 無限に実行するための待機

if __name__ == "__main__":
    asyncio.run(main())
