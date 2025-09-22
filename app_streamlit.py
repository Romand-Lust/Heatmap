import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

# Ordner für Heatmaps
os.makedirs("outputs/heatmaps", exist_ok=True)

# Session State für Ergebnisse
if "results" not in st.session_state:
    st.session_state.results = []

# Analyse-Funktion (zurück auf "Normalzustand")
def analyze_video(video_path, video_id):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("❌ Fehler: Video konnte nicht geöffnet werden.")
        return None, None, None

    ret, frame = cap.read()
    heatmap_accum = np.zeros_like(frame[:, :, 0], dtype=np.float32)

    while ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, cv2.medianBlur(gray, 5))  # Bewegung hervorheben
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        heatmap_accum += thresh.astype(np.float32)
        ret, frame = cap.read()

    cap.release()

    # Heatmap zurück zum Normalzustand (direkt mit cv2.COLORMAP_JET einfärben)
    heatmap_uint8 = np.clip(heatmap_accum, 0, 255).astype(np.uint8)
    heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

    heatmap_filename = f"outputs/heatmaps/heatmap_{video_id}.png"
    cv2.imwrite(heatmap_filename, heatmap_colored)

    # Score berechnen
    active_pixels = np.sum(heatmap_uint8 > 50)
    score = min(int(active_pixels / 100), 100)

    # Level bestimmen
    if score < 30:
        level = "Bronze 🥉"
    elif score < 70:
        level = "Silver 🥈"
    else:
        level = "Gold 🥇"

    return heatmap_filename, score, level

# ----------------- Streamlit App -----------------

st.title("🐾 Cat Heatmap Analyzer")

st.info("ℹ️ Bitte achte darauf, dass die Kamera beim Filmen **still gehalten** wird.")

uploaded_file = st.file_uploader("📤 Lade ein Video hoch (MP4)", type=["mp4"])

if uploaded_file is not None:
    # Temporäre Datei speichern
    video_path = f"temp_{uploaded_file.name}"
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Zeigen, dass Analyse läuft
    with st.spinner("🔍 Video wird analysiert... bitte warten"):
        video_id = len(st.session_state.results) + 1
        heatmap, score, level = analyze_video(video_path, video_id)

    if heatmap is not None:
        # Original Video anzeigen
        st.video(video_path)

        # Heatmap anzeigen (jetzt wieder wie vorher)
        st.image(heatmap, caption="🔥 Heatmap Ergebnis", use_container_width=True)

        # Ergebnisse speichern
        st.session_state.results.append({
            "Nummer": video_id,
            "Datei": uploaded_file.name,
            "Score": score,
            "Level": level
        })

        # Tabelle anzeigen
        df = pd.DataFrame(st.session_state.results)
        st.subheader("📊 Übersicht")
        st.dataframe(df, use_container_width=True)

        # Score-Verlauf anzeigen
        st.subheader("📈 Score Verlauf")
        fig, ax = plt.subplots()
        ax.plot(df["Nummer"], df["Score"], marker="o", linestyle="-", color="blue")
        ax.set_xlabel("Nummer")
        ax.set_ylabel("Score")
        ax.set_xticks(df["Nummer"])
        st.pyplot(fig)
