import asyncio
import websockets
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--address", help="Server address", default="localhost")

async def time_server(websocket, path):
    prevData = ""
    while True:
        try:
            # people_results.jsonファイルの内容を読み取る
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
        # 10ms待機してから再度ファイルを読み取る
        await asyncio.sleep(0.01)

args = parser.parse_args()
address = args.address

start_server = websockets.serve(time_server, address, 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
