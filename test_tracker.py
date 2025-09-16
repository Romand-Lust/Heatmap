from tracker import detect_motion, save_heatmap

video_path = "data/test_video_2.mp4"  # Ersetze durch deinen Pfad
heatmap = detect_motion(video_path)
save_heatmap(heatmap, "data/heatmap_output_1.png")

print("✅ Heatmap wurde erzeugt und gespeichert.")
