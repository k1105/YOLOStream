import subprocess
import argparse
import os

def run_scripts(address, mirrored):

    venv = os.path.join(os.environ['VIRTUAL_ENV'], 'bin', 'python')

    # tracker.py を実行時の引数に基づいて実行
    tracker_cmd = [venv, "tracker.py"]

    if mirrored:
        tracker_cmd.append("--mirrored")
    tracker_process = subprocess.Popen(tracker_cmd)

    # sender.py を実行時の引数に基づいて実行
    people_sender_cmd = [venv, "send_people.py", "--address", address]
    people_sender_process = subprocess.Popen(people_sender_cmd)
    pose_sender_cmd = [venv, "send_pose.py", "--address", address]
    pose_sender_process = subprocess.Popen(pose_sender_cmd)

    # audio_player_cmd = [venv, "audio_player.py", "--address", address]
    # audio_player_process = subprocess.Popen(audio_player_cmd)

    # 両方のプロセスが終了するまで待機
    tracker_process.wait()
    people_sender_process.wait()
    pose_sender_process.wait()
    # audio_player_process.wait()

if __name__ == "__main__":
    # コマンドライン引数のパーサーを設定
    parser = argparse.ArgumentParser(description="Run tracker and sender scripts")
    parser.add_argument("--address", help="Server address", default="localhost")
    parser.add_argument("--mirrored", help="Enable mirrored mode for tracker", action="store_true")

    # 引数をパース
    args = parser.parse_args()

    # パースした引数をそれぞれのスクリプトに渡して実行
    run_scripts(args.address, args.mirrored)
