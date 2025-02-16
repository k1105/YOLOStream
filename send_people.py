import asyncio
import websockets
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--address", help="Server address", default="localhost")
args = parser.parse_args()
address = args.address

async def time_server(websocket, path):
    prevData = ""
    while True:
        try:
            with open("people_results.json", "r") as file:
                data = json.load(file)

            if data != prevData:
                await websocket.send(json.dumps(data))
                print(f"SENT DATA")

        except FileNotFoundError:
            print("people_results.json not found.")
        except json.decoder.JSONDecodeError:
            print("json decode error.")

        prevData = data
        await asyncio.sleep(0.01)

async def main():
    async with websockets.serve(time_server, address, 8765):
        print(f"WebSocket server started on {address}:8765")
        await asyncio.Future()  # 無限に実行するための待機

if __name__ == "__main__":
    asyncio.run(main())  # ここで適切にイベントループを開始
