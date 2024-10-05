import asyncio
import websockets
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--address", help="Server address", default="localhost")
parser.add_argument("--port", help="Server port", type=int, default=8765)  # ポートもオプションで指定できるように

async def time_server(websocket, path):
    prevData = ""

    while True:
        try:
            # yolo_results.jsonファイルの内容を読み取る
            with open("yolo_results.json", "r") as file:
                data = json.load(file)

            if data != prevData:
                await websocket.send(json.dumps(data))
                print(f"SENT DATA")

        except FileNotFoundError:
            print("yolo_results.json not found.")
        except json.decoder.JSONDecodeError:
            print("json decode error.")

        prevData = data
        # 10ms待機してから再度ファイルを読み取る
        await asyncio.sleep(0.01)

args = parser.parse_args()
address = args.address
port = args.port

start_server = websockets.serve(time_server, address, port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
