import os
from analyzer import analyze_video

video_folder = "data/videos"
video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]

if not os.path.exists(video_folder):
    print(f"❌ Ordner '{video_folder}' nicht gefunden.")
    exit()

for video in video_files:
    full_path = os.path.join(video_folder, video)
    analyze_video(full_path)
