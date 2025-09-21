import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import cv2
import numpy as np
import random
from pathlib import Path

st.set_page_config(page_title="Video Analyse", layout="centered")

# Session State für Ergebnisse
if "results" not in st.session_state:
    st.session_state.results = []

st.title("🎥 Video Analyse mit Heatmap")

st.info("Bitte halte die Kamera beim Filmen **stabil** für die beste Analyse.")

uploaded_file = st.file_uploader("Lade ein Video hoch", type=["mp4", "mov", "avi"])

def analyze_video(file, video_id):
    # Video temporär speichern
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(file.read())
    video_path = tfile.name

    with st.spinner("⏳ Video wird analysiert ..."):
        cap = cv2.VideoCapture(video_path)
        frames = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames.append(gray)

        cap.release()

        if frames:
            avg_frame = np.mean(frames, axis=0).astype(np.uint8)
            heatmap = cv2.applyColorMap(avg_frame, cv2.COLORMAP_JET)

            heatmap_path = Path(tempfile.gettempdir()) / f"heatmap_{video_id}.png"
            cv2.imwrite(str(heatmap_path), heatmap)
        else:
            heatmap_path = None

        # Dummy Score
        score = random.randint(20, 100)

        # Level bestimmen
        if score < 40:
            level = "Bronze"
        elif score < 60:
            level = "Silber"
        elif score < 80:
            level = "Gold"
        else:
            level = "Platin"

    return str(heatmap_path), score, level

if uploaded_file is not None:
    # Video anzeigen
    st.subheader("📹 Hochgeladenes Video")
    st.video(uploaded_file)

    # Analyse starten
    video_id = len(st.session_state.results) + 1
    heatmap, score, level = analyze_video(uploaded_file, video_id)

    # Heatmap anzeigen
    if heatmap:
        st.subheader("🔥 Heatmap")
        st.image(heatmap, caption="Analyse-Ergebnis", use_container_width=True)

    # Ergebnisse speichern
    st.session_state.results.append({
        "Nummer": video_id,
        "Datei": uploaded_file.name,
        "Score": score,
        "Level": level
    })

# Ergebnisse darstellen
if st.session_state.results:
    st.subheader("📊 Übersicht")
    df = pd.DataFrame(st.session_state.results)
    st.table(df)

    # Score-Verlauf
    st.subheader("📈 Score Verlauf")
    fig, ax = plt.subplots()
    ax.plot(df["Nummer"], df["Score"], marker="o", linestyle="-")
    ax.set_xlabel("Nummer")
    ax.set_ylabel("Score")
    ax.set_title("Score Entwicklung pro Video")
    st.pyplot(fig)


