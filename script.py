import streamlit as st
import requests
import time

# Paste your AssemblyAI API key here:
ASSEMBLYAI_API_KEY = "404746088d65442d9272e65b1667ca8b"

HEADERS = {
    "authorization": ASSEMBLYAI_API_KEY,
    "content-type": "application/json"
}

TRANSCRIPT_ENDPOINT = "https://api.assemblyai.com/v2/transcript"

def request_transcription(audio_url):
    json = {
        "audio_url": audio_url,
        "auto_chapters": False,
        "language_code": "en_us"
    }
    response = requests.post(TRANSCRIPT_ENDPOINT, json=json, headers=HEADERS)
    response.raise_for_status()
    return response.json()["id"]

def get_transcription_result(transcript_id):
    url = f"{TRANSCRIPT_ENDPOINT}/{transcript_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def main():
    st.title("Accent Classification Helper (AssemblyAI)")
    st.markdown("""
        Enter a public video/audio URL (MP4, MP3, etc.) to extract audio and transcribe it.
        The transcription can then be used for accent analysis.
    """)

    audio_url = st.text_input("Paste your public video/audio URL here(not a youtube url:")

    if st.button("Submit for Transcription"):
        if not audio_url:
            st.error("Please enter a valid URL.")
            return

        with st.spinner("Submitting transcription request..."):
            try:
                transcript_id = request_transcription(audio_url)
                st.success(f"Transcription requested! Transcript ID: {transcript_id}")
            except Exception as e:
                st.error(f"Error submitting transcription: {e}")
                return

        st.info("Polling for transcription result...")

        while True:
            time.sleep(5)  # Wait 5 seconds before polling
            result = get_transcription_result(transcript_id)
            status = result["status"]

            if status == "completed":
                st.success("Transcription completed!")
                st.text_area("Transcription Text", result["text"], height=300)
                # Here you can add your accent classification logic based on result["text"]
                break
            elif status == "error":
                st.error(f"Transcription failed: {result['error']}")
                break
            else:
                st.write(f"Transcription status: {status}. Checking again in 5 seconds...")

if __name__ == "__main__":
    main()
