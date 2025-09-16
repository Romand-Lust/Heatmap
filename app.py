# app.py
import streamlit as st
from tracker import detect_motion, save_heatmap

st.title("🐾 Katzen-Heatmap Tracker")

video = st.file_uploader("Lade dein 2-Minuten Video hoch", type=["mp4"])

if video:
    with open("data/video.mp4", "wb") as f:
        f.write(video.read())

    if st.button("🏃 Tracking starten"):
        heatmap = detect_motion("data/video.mp4")
        save_heatmap(heatmap, "data/heatmap.png")
        st.image("data/heatmap.png", caption="Aktivitäts-Heatmap")
