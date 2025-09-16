import streamlit as st
import cv2
import numpy as np
import os
import pandas as pd
from datetime import datetime
from tracker import detect_motion
from medaillen import calculate_activity_score, get_activity_level
import matplotlib.pyplot as plt

# Speicher für Ergebnisse
if "results" not in st.session_state:
    st.session_state.results = []
    st.session_state.video_counter = 0

st.title("🐾 Katzen Aktivitäts-Analyse")

# Hinweis anzeigen
st.info("Bitte halte die Kamera während der Aufnahme möglichst **stabil**, "
        "damit die Bewegungen der Katze korrekt erkannt werden.")

# Datei-Upload
uploaded_file = st.file_uploader("Lade ein Video hoch", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Video temporär speichern
    temp_video_path = "temp_video.mp4"
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.read())

    # Originalvideo anzeigen
    st.video(temp_video_path)

    # Analyse starten
    with st.spinner("⏳ Video wird analysiert ..."):
        heatmap = detect_motion(temp_video_path)

        if heatmap is not None:
            # Score & Level berechnen
            score = calculate_activity_score(heatmap)
            level = get_activity_level(score)

            # Heatmap wie vorher einfärben
            heatmap_img = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
            heatmap_img = np.uint8(heatmap_img)
            heatmap_colored = cv2.applyColorMap(heatmap_img, cv2.COLORMAP_JET)
            heatmap_rgb = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

            # Heatmap speichern
            os.makedirs("outputs/heatmaps", exist_ok=True)
            filename = f"outputs/heatmaps/heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            cv2.imwrite(filename, heatmap_colored)

            # Video-Nr. hochzählen
            st.session_state.video_counter += 1
            video_nr = st.session_state.video_counter

            # Ergebnisse speichern
            st.session_state.results.append({
                "Nr": video_nr,
                "Datei": uploaded_file.name,
                "Score": score,
                "Level": level
            })

            # Ergebnisse anzeigen
            st.success(f"🎯 Score: {score}/100")
            st.write(f"🏅 Level: {level}")
            st.image(heatmap_rgb, caption="Heatmap", use_container_width=True)
            st.caption(f"✅ Heatmap gespeichert: {filename}")

        else:
            st.error("❌ Fehler beim Verarbeiten des Videos.")

# Wenn Ergebnisse da sind → Tabelle & Diagramm
if len(st.session_state.results) > 0:
    df = pd.DataFrame(st.session_state.results)

    st.subheader("📊 Übersicht")
    st.dataframe(df[["Nr", "Datei", "Score", "Level"]], use_container_width=True)

    # Liniendiagramm mit Ganzzahlen auf der x-Achse
    st.subheader("📈 Score-Verlauf")
    fig, ax = plt.subplots()
    ax.plot(df["Nr"], df["Score"], marker="o", linestyle="-")
    ax.set_xlabel("Nummer")
    ax.set_ylabel("Score")
    ax.set_xticks(df["Nr"])  # Ganzzahlen erzwingen
    st.pyplot(fig)
