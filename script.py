import streamlit as st
import requests
import tempfile
from moviepy.editor import VideoFileClip

ASSEMBLY_API_KEY = "404746088d65442d9272e65b1667ca8b"

def extract_audio(video_url):
    video_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")

    # Download video
    with open(video_path.name, 'wb') as f:
        f.write(requests.get(video_url).content)

    # Extract audio
    video = VideoFileClip(video_path.name)
    video.audio.write_audiofile(audio_path.name)
    return audio_path.name

def upload_audio_to_assembly(audio_file):
    headers = {'authorization': ASSEMBLY_API_KEY}
    with open(audio_file, 'rb') as f:
        response = requests.post("https://api.assemblyai.com/v2/upload", headers=headers, files={'file': f})
    return response.json()['upload_url']

def request_transcription(upload_url):
    endpoint = "https://api.assemblyai.com/v2/transcript"
    json = {
        "audio_url": upload_url,
        "auto_chapters": False,
        "speaker_labels": True
    }
    headers = {
        "authorization": ASSEMBLY_API_KEY,
        "content-type": "application/json"
    }
    response = requests.post(endpoint, json=json, headers=headers)
    return response.json()['id']

def get_transcription_result(transcript_id):
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    headers = {"authorization": ASSEMBLY_API_KEY}
    while True:
        response = requests.get(endpoint, headers=headers)
        result = response.json()
        if result['status'] == 'completed':
            return result
        elif result['status'] == 'error':
            raise Exception(result['error'])

def main():
    st.title("English Accent Detection Tool")
    video_url = st.text_input("Enter the public video URL (MP4, Loom, etc.):")

    if video_url and st.button("Analyze Accent"):
        st.info("Extracting audio...")
        audio_file = extract_audio(video_url)
        
        st.info("Uploading to AssemblyAI...")
        audio_url = upload_audio_to_assembly(audio_file)
        
        st.info("Requesting transcription & accent analysis...")
        transcript_id = request_transcription(audio_url)
        result = get_transcription_result(transcript_id)
        
        st.success("Analysis complete!")
        st.write("**Transcript:**", result.get("text", "N/A"))
        st.write("**Accent classification not directly available**, but you can infer speaker geography from speaker labels (in production, fine-tune using prosody + pitch analysis).")

if __name__ == "__main__":
    main()
