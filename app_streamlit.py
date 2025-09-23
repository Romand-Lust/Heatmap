import streamlit as st
import cv2
import numpy as np
import os
import pandas as pd
from datetime import datetime
from tracker import detect_motion
from medaillen import calculate_activity_score, get_activity_level
import matplotlib.pyplot as plt

# Storage for results
if "results" not in st.session_state:
    st.session_state.results = []
    st.session_state.video_counter = 0

st.title("🐾 Cat Activity Analysis")

# Upload Instructions
st.markdown("""
### 📹 Video Upload Instructions
1. Keep the camera **stable** – no panning or zooming.  
2. Make sure the **cat is clearly visible**.  
3. Upload only short clips (10–30 seconds recommended).  

➡️ Click **Choose file** below to upload your video.
""")

# File uploader
uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    # Save video temporarily
    temp_video_path = "temp_video.mp4"
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.read())

    # Show original video
    st.video(temp_video_path)

    # Analyze video
    with st.spinner("⏳ Analyzing video..."):
        heatmap = detect_motion(temp_video_path)

        if heatmap is not None:
            # Score & Level
            score = calculate_activity_score(heatmap)
            level = get_activity_level(score)

            # Colored Heatmap
            heatmap_img = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
            heatmap_img = np.uint8(heatmap_img)
            heatmap_colored = cv2.applyColorMap(heatmap_img, cv2.COLORMAP_JET)
            heatmap_rgb = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

            # Save Heatmap
            os.makedirs("outputs/heatmaps", exist_ok=True)
            filename = f"outputs/heatmaps/heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            cv2.imwrite(filename, heatmap_colored)

            # Video number
            st.session_state.video_counter += 1
            video_nr = st.session_state.video_counter

            # Save results
            st.session_state.results.append({
                "Nr": video_nr,
                "File": uploaded_file.name,
                "Score": score,
                "Level": level
            })

            # Level display with colors
            level_colors = {
                "Bronze": "🥉 Bronze",
                "Silver": "🥈 Silver",
                "Gold": "🥇 Gold",
                "Platinum": "🏆 Platinum"
            }

            st.success(f"🎯 Score: {score}/100" f"🏅 Level: {level_colors.get(level, level)}")  

            # Tabs for better layout
            tab1, tab2, tab3 = st.tabs(["🔥 Heatmap", "📊 Overview", "📈 Score Trend"])

            # Overview Tab
            with tab1:
                st.image(heatmap_rgb, caption="Heatmap", use_container_width=True)
                st.caption(f"✅ Heatmap saved: {filename}")
               
            # Heatmap Tab
            with tab2:
                df = pd.DataFrame(st.session_state.results)
                st.dataframe(df[["Nr", "File", "Score", "Level"]], use_container_width=True)

            # Score Trend Tab
            with tab3:
                if len(st.session_state.results) > 0:
                    df = pd.DataFrame(st.session_state.results)
                    fig, ax = plt.subplots()
                    ax.plot(df["Nr"], df["Score"], marker="o", linestyle="-")
                    ax.set_xlabel("Number")
                    ax.set_ylabel("Score")
                    ax.set_xticks(df["Nr"])  # enforce whole numbers
                    st.pyplot(fig)

        else:
            st.error("❌ Error processing the video.")
