import json
import os

def load_folder(folder_path):
    json_path = os.path.join(folder_path, "mediapipe_data_full.json")
    video_path = os.path.join(folder_path, "video_processed.mp4")
    if not os.path.exists(json_path):
        raise FileNotFoundError("mediapipe_data_full.json not found")
    if not os.path.exists(video_path):
        raise FileNotFoundError("video_processed.mp4 not found")
    with open(json_path,"r") as f:
        data = json.load(f)["values"]
    return data, video_path
