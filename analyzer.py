import cv2
import numpy as np
import os
from datetime import datetime
from medaillen import calculate_activity_score, get_activity_level

def analyze_video(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("❌ Fehler: Video konnte nicht geöffnet werden.")
        return None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Leere Heatmap
    heatmap = np.zeros((height, width), dtype=np.float32)

    # Hintergrund-Subtraktor
    fgbg = cv2.createBackgroundSubtractorMOG2()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        fgmask = fgbg.apply(frame)

        # Bewegung hinzufügen
        heatmap += fgmask

    cap.release()

    # Score & Level berechnen
    score = calculate_activity_score(heatmap)
    level = get_activity_level(score)

    # Heatmap speichern
    heatmap_img = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heatmap_img = np.uint8(heatmap_img)
    heatmap_colored = cv2.applyColorMap(heatmap_img, cv2.COLORMAP_JET)

    os.makedirs("outputs/heatmaps", exist_ok=True)
    filename = f"outputs/heatmaps/heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    cv2.imwrite(filename, heatmap_colored)

    print(f"📊 Aktive Pixel berechnet – Score: {score}, Level: {level}")
    print(f"✅ Heatmap gespeichert: {filename}")

    return heatmap, score, level, filename
