import asyncio
import websockets
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--address", help="Server address", default="localhost")

async def send_pose_data(websocket, path):
    prevData = ""
    while True:
        try:
            with open("pose_results.json", "r") as file:
                data = json.load(file)

            if data != prevData:
                await websocket.send(json.dumps(data))
                print(f"Sent pose data: {data}")

            prevData = data
        except FileNotFoundError:
            print("pose_results.json not found.")
        except json.decoder.JSONDecodeError:
            print("json decode error.")
        await asyncio.sleep(0.01)

args = parser.parse_args()
address = args.address

start_server = websockets.serve(send_pose_data, address, 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
