import streamlit as st
import os
import tempfile
from elevenlabs_stt import transcribe_file
from dotenv import load_dotenv

load_dotenv()

st.title("Audio Transcriber")

audio_file = st.file_uploader("Audio File", type=["mp3", "wav", "mp4", "m4a", "ogg", "webm"])

if st.button("Transcribe"):
    if audio_file is None:
        st.warning("Please upload an audio file.")
    else:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            st.error("ELEVENLABS_API_KEY not found in .env file.")
        else:
            with st.spinner("Transcribing..."):
                # Save uploaded file to a temp file
                suffix = os.path.splitext(audio_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(audio_file.read())
                    tmp_path = tmp.name

                result = transcribe_file(tmp_path, api_key=api_key)
                os.unlink(tmp_path)

            st.text_area("Textual O/P", value=result.get("text", ""), height=300)
