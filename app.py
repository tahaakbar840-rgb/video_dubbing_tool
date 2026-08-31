import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from modules.audio_extractor import extract_audio
from modules.transcriber import transcribe_audio
from modules.translator import translate_segments
from modules.subtitle_burner import generate_srt, burn_subtitles
import os
import streamlit as st
from modules.audio_extractor import extract_audio
from modules.transcriber import transcribe_audio
from modules.translator import translate_segments
from modules.subtitle_burner import generate_srt, burn_subtitles

# Page Configuration
st.set_page_config(
    page_title="AI Video Subtitling & Dubbing Platform",
    page_icon="🎬",
    layout="centered"
)

# Directories setup
TEMP_DIR = "temp"
OUTPUT_DIR = "outputs"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# App UI Header
st.title("🎬 AI Video Subtitling & Dubbing Platform")
st.markdown("<p style='text-align: center;'>Upload a video file to transcribe, translate, and hardcode subtitles seamlessly.</p>", unsafe_allow_html=True)

# Inputs
uploaded_video = st.file_uploader("Upload Input Video", type=["mp4", "mkv", "avi", "mov"])

col1, col2 = st.columns(2)
with col1:
    target_lang = st.selectbox(
        "Target Subtitle Language",
        options=["en", "ur", "ar", "es", "fr", "de", "hi"],
        format_func=lambda x: {
            "en": "English",
            "ur": "Urdu",
            "ar": "Arabic",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "hi": "Hindi"
        }.get(x, x)
    )
with col2:
    model_size = st.selectbox("Whisper Model Size", ["tiny", "base", "small", "medium"])

# Processing Logic
if st.button("🚀 Start Processing Video"):
    if uploaded_video is not None:
        video_path = os.path.join(TEMP_DIR, uploaded_video.name)
        audio_path = os.path.join(TEMP_DIR, "extracted_audio.wav")
        srt_path = os.path.join(TEMP_DIR, "subtitles.srt")
        output_video_path = os.path.join(OUTPUT_DIR, f"subtitled_{uploaded_video.name}")

        with open(video_path, "wb") as f:
            f.write(uploaded_video.getbuffer())

        try:
            status = st.status("Processing Video...", expanded=True)
            
            status.write("Step 1/4: Extracting Audio from Video...")
            extract_audio(video_path, audio_path)
            
            status.write("Step 2/4: Transcribing Audio with Whisper...")
            segments = transcribe_audio(audio_path, model_size=model_size)
            
            status.write("Step 3/4: Translating Subtitles...")
            translated_segments = translate_segments(segments, target_lang=target_lang)
            
            status.write("Step 4/4: Burning Subtitles onto Video...")
            generate_srt(translated_segments, srt_path, lang=target_lang)
            burn_subtitles(video_path, srt_path, output_video_path)
            
            status.update(label="Processing Complete!", state="complete", expanded=False)
            
            st.success("🎉 Video Processed Successfully!")
            st.video(output_video_path)
            
        except Exception as e:
            st.error(f"Processing Failed! Error: {str(e)}")
    else:
        st.warning("Please upload a video file first.")