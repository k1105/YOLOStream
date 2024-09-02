import asyncio
import websockets
import json

async def time_server(websocket, path):
    prevData = ""

    while True:
        try:
            # yolo_results.jsonファイルの内容を読み取る
            with open("yolo_results.json", "r") as file:
                data = json.load(file)

            if data != prevData:
                await websocket.send(json.dumps(data))
                print(f"Sent data: {data}")

        except FileNotFoundError:
            print("yolo_results.json not found.")
        except json.decoder.JSONDecodeError:
            print("json decode error.")

        prevData = data
        # 10ms待機してから再度ファイルを読み取る
        await asyncio.sleep(0.01)

start_server = websockets.serve(time_server, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
