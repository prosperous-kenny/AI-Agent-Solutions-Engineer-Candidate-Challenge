import streamlit as st
import tempfile
import os
import torch
import torchaudio
from moviepy.editor import VideoFileClip
from speechbrain.pretrained import SpeakerRecognition
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import urllib.request

# Load ECAPA-TDNN model from SpeechBrain
@st.cache_resource
def load_model():
    return SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")

model = load_model()

# Dictionary of accent embeddings (mock data for now)
ACCENT_EMBEDDINGS = {
    "American": torch.rand(1, 192),
    "British": torch.rand(1, 192),
    "Australian": torch.rand(1, 192)
}

def extract_audio_from_video(video_url):
    tmp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    urllib.request.urlretrieve(video_url, tmp_video.name)
    clip = VideoFileClip(tmp_video.name)
    tmp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    clip.audio.write_audiofile(tmp_audio.name, codec='pcm_s16le')
    return tmp_audio.name

def get_embedding(audio_path):
    return model.encode_batch(model.load_audio(audio_path)).squeeze(0)

def classify_accent(embedding):
    best_score = -1
    best_label = "Unknown"
    for label, ref_embedding in ACCENT_EMBEDDINGS.items():
        score = cosine_similarity(embedding.unsqueeze(0), ref_embedding)[0][0]
        if score > best_score:
            best_score = score
            best_label = label
    return best_label, best_score * 100

st.set_page_config(page_title="Accent Classifier", layout="centered")
st.title("English Accent Detection Tool")

video_url = st.text_input("Enter a public video URL (MP4 or Loom)")

if st.button("Analyze") and video_url:
    try:
        st.info("Downloading and processing the video...")
        audio_path = extract_audio_from_video(video_url)

        st.info("Extracting voice embeddings...")
        embedding = get_embedding(audio_path)

        st.info("Classifying accent...")
        label, score = classify_accent(embedding)

        st.success(f"**Detected Accent:** {label}")
        st.metric(label="Confidence Score", value=f"{score:.2f}%")
        st.caption("*This tool uses voice embedding similarity for rough accent classification.*")

        os.remove(audio_path)
    except Exception as e:
        st.error(f"Something went wrong: {e}")
