import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cv2
import tempfile
import datetime

# --- Page Setup ---
st.set_page_config(page_title="Cat Activity Heatmap Analyzer", layout="centered")

st.title("🐾 Cat Activity Heatmap Analyzer")
st.write("Upload a video of your cat, and we’ll generate a **heatmap**, an **activity score**, and assign a **level**.")
st.info("📌 Tip: For best results, keep the camera **steady** while recording.")

# --- Session State ---
if "results" not in st.session_state:
    st.session_state.results = []
    st.session_state.counter = 0

# --- File Upload ---
uploaded_file = st.file_uploader("📂 Upload a video", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    st.video(uploaded_file)

    with st.spinner("⏳ Analyzing your video... please wait."):
        # Save file temporarily
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        video_path = tfile.name

        # --- Generate Heatmap (very simple example) ---
        cap = cv2.VideoCapture(video_path)
        heatmap = None
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if heatmap is None:
                heatmap = np.float32(gray)
            else:
                heatmap += gray
        cap.release()

        heatmap_norm = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap_img = np.uint8(heatmap_norm)

        # --- Calculate Score ---
        score = int(np.mean(heatmap_norm))
        if score < 85:
            level = "🥉 Bronze"
        elif score < 170:
            level = "🥈 Silver"
        else:
            level = "🥇 Gold"

        # --- Save Result ---
        st.session_state.counter += 1
        st.session_state.results.append({
            "Number": st.session_state.counter,
            "File Name": uploaded_file.name,
            "Score": score,
            "Level": level
        })

    # --- Show Results ---
    st.subheader("📊 Results")

    st.image(heatmap_img, caption="Heatmap", use_column_width=True)

    df = pd.DataFrame(st.session_state.results)
    st.table(df)

    # --- Score Chart ---
    st.subheader("📈 Score Progression")
    fig, ax = plt.subplots()
    ax.plot(df["Number"], df["Score"], marker="o", linestyle="-")
    ax.set_xlabel("Number")
    ax.set_ylabel("Score")
    ax.set_xticks(df["Number"])  # force integer ticks only
    st.pyplot(fig)
