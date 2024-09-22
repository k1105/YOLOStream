import subprocess
import argparse

def run_scripts(address, port, mirrored):
    # tracker.py を実行時の引数に基づいて実行
    tracker_cmd = ["python", "tracker.py"]
    if mirrored:
        tracker_cmd.append("--mirrored")
    tracker_process = subprocess.Popen(tracker_cmd)

    # sender.py を実行時の引数に基づいて実行
    sender_cmd = ["python", "sender.py", "--address", address, "--port", str(port)]
    sender_process = subprocess.Popen(sender_cmd)

    # 両方のプロセスが終了するまで待機
    tracker_process.wait()
    sender_process.wait()

if __name__ == "__main__":
    # コマンドライン引数のパーサーを設定
    parser = argparse.ArgumentParser(description="Run tracker and sender scripts")
    parser.add_argument("--address", help="Server address", default="localhost")
    parser.add_argument("--port", help="Server port", type=int, default=8765)
    parser.add_argument("--mirrored", help="Enable mirrored mode for tracker", action="store_true")

    # 引数をパース
    args = parser.parse_args()

    # パースした引数をそれぞれのスクリプトに渡して実行
    run_scripts(args.address, args.port, args.mirrored)
