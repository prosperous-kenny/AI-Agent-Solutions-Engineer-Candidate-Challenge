import streamlit as st
from moviepy.editor import VideoFileClip
import tempfile
import os
import requests
import time

ASSEMBLYAI_API_KEY = st.secrets["404746088d65442d9272e65b1667ca8b"]

def extract_audio(video_url):
    temp_dir = tempfile.mkdtemp()
    video_path = os.path.join(temp_dir, "video.mp4")
    audio_path = os.path.join(temp_dir, "audio.wav")

    with open(video_path, "wb") as f:
        f.write(requests.get(video_url).content)

    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path)

    return audio_path

def upload_to_assemblyai(audio_path):
    headers = {'authorization': ASSEMBLYAI_API_KEY}
    with open(audio_path, 'rb') as f:
        response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=f)
    return response.json()['upload_url']

def transcribe_with_accent_detection(audio_url):
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json = {
        "audio_url": audio_url,
        "speaker_labels": True,
        "language_detection": True,
        "auto_chapters": False,
        "iab_categories": False
    }
    headers = {
        "authorization": ASSEMBLYAI_API_KEY,
        "content-type": "application/json"
    }
    response = requests.post(endpoint, json=json, headers=headers)
    transcript_id = response.json()['id']

    # Polling
    polling_endpoint = f"{endpoint}/{transcript_id}"
    while True:
        poll_response = requests.get(polling_endpoint, headers=headers).json()
        if poll_response['status'] == 'completed':
            return poll_response
        elif poll_response['status'] == 'error':
            return {"error": poll_response['error']}
        time.sleep(3)

def summarize_accent(metadata):
    detected_lang = metadata.get("language_code", "unknown")
    confidence = metadata.get("confidence", 0)
    accent_map = {
        "en_us": "American",
        "en_uk": "British",
        "en_au": "Australian",
    }
    accent = accent_map.get(detected_lang, "Unknown")
    return {
        "accent": accent,
        "confidence": round(confidence * 100, 2),
        "summary": f"Detected accent is likely {accent} based on language code '{detected_lang}'."
    }

st.title("Accent Detection Tool (via AssemblyAI)")

video_url = st.text_input("Enter a video URL (MP4 format)")

if st.button("Analyze Accent") and video_url:
    with st.spinner("Processing video..."):
        audio_path = extract_audio(video_url)
        audio_url = upload_to_assemblyai(audio_path)
        metadata = transcribe_with_accent_detection(audio_url)
        result = summarize_accent(metadata)

    if "error" in metadata:
        st.error(f"Error: {metadata['error']}")
    else:
        st.success(f"Accent: {result['accent']}")
        st.write(f"Confidence: {result['confidence']}%")
        st.write(result["summary"])
