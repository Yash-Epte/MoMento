import streamlit as st
import os
import tempfile
import json
from groq import Groq
from elevenlabs_stt import transcribe_file
from dotenv import load_dotenv

load_dotenv()

# Configure Groq
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

st.set_page_config(page_title="Meeting Transcriber", layout="wide")
st.title("Meeting Transcriber & Task Summarizer")

# ── Step 1: Upload & Transcribe ──────────────────────────────────────────────
audio_file = st.file_uploader("Audio File", type=["mp3", "wav", "mp4", "m4a", "ogg", "webm"])

if st.button("Transcribe"):
    if audio_file is None:
        st.warning("Please upload an audio file.")
    else:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            st.error("ELEVENLABS_API_KEY not found in .env file.")
        else:
            with st.spinner("Transcribing audio..."):
                suffix = os.path.splitext(audio_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(audio_file.read())
                    tmp_path = tmp.name

                result = transcribe_file(tmp_path, api_key=api_key)
                os.unlink(tmp_path)

            transcript = result.get("text", "")
            st.session_state["transcript"] = transcript

# ── Step 2: Show transcript text box ─────────────────────────────────────────
transcript = st.session_state.get("transcript", "")
text = st.text_area("Transcript Text", value=transcript, height=120)

# ── Step 3: Parse with Groq ───────────────────────────────────────────────────
if st.button("Summarize Tasks"):
    if not text.strip():
        st.warning("No text to summarize. Please transcribe audio first or paste text.")
    else:
        if not os.environ.get("GROQ_API_KEY"):
            st.error("GROQ_API_KEY not found in .env file.")
        else:
            with st.spinner("Analyzing tasks per person..."):

                prompt = f"""You are a meeting assistant. Analyze the following meeting transcript and extract:
1. Every person mentioned by name
2. Their individual tasks, action items, and agenda points

Return ONLY a valid JSON object in this exact format (no extra text, no markdown, no code fences):
{{
  "people": [
    {{
      "name": "Person Name",
      "summary": "Brief overall summary of their role/discussion",
      "tasks": ["Task 1", "Task 2", "Task 3"]
    }}
  ]
}}

Transcript:
{text}"""

                try:
                    completion = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.2,
                    )
                    raw = completion.choices[0].message.content.strip()

                    # Strip markdown code fences if present
                    if raw.startswith("```"):
                        raw = raw.split("```")[1]
                        if raw.startswith("json"):
                            raw = raw[4:]
                    raw = raw.strip()

                    data = json.loads(raw)
                    st.session_state["people"] = data.get("people", [])

                except json.JSONDecodeError as e:
                    st.error(f"Failed to parse JSON response from Groq: {e}")
                    st.code(raw, language="text")
                except Exception as e:
                    st.error(f"Groq API error: {e}")

# ── Step 4: Display per-person columns ───────────────────────────────────────
people = st.session_state.get("people", [])
if people:
    st.markdown("---")
    cols = st.columns(len(people))
    for col, person in zip(cols, people):
        with col:
            st.subheader(person["name"])
            st.markdown(f"**Summary:** {person['summary']}")
            st.markdown("**Tasks:**")
            for task in person.get("tasks", []):
                st.markdown(f"- {task}")