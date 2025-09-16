import cv2
import numpy as np

def detect_motion(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame1 = cap.read()
    if not ret:
        print("Video konnte nicht geladen werden.")
        return None

    frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    height, width = frame1_gray.shape
    heatmap = np.zeros((height, width), dtype=np.float32)

    while True:
        ret, frame2 = cap.read()
        if not ret:
            break

        frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(frame1_gray, frame2_gray)
        _, thresh = cv2.threshold(diff, 25, 1, cv2.THRESH_BINARY)
        heatmap += thresh.astype(np.float32)

        frame1_gray = frame2_gray

    cap.release()
    return heatmap
