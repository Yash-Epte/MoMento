# MoMento — Meeting Transcriber & Action Items

MoMento is a Streamlit app that turns a meeting recording into **per-person summaries and action items**.

**How it works**
- **Audio → text**: ElevenLabs Speech-to-Text (`scribe_v2`)
- **Transcript → structured tasks**: Groq LLM extracts a JSON list of participants, each with a summary + tasks
- **UI**: action items grouped by person, searchable, with a priority selector (High/Medium/Low)

## Setup

```bash
cd "Project_meet"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```bash
touch .env
```

Add these environment variables:

```bash
ELEVENLABS_API_KEY=...
GROQ_API_KEY=...
```

## Run

### Streamlit app (recommended)

```bash
streamlit run app.py
```

Then upload an audio file (e.g. `mp3`) and click **Transcribe & Summarize**.

### CLI: transcribe audio (optional)

```bash
python3 elevenlabs_stt.py ./audio.mp3
python3 elevenlabs_stt.py ./audio.wav --diarize --language-code en --out-json transcript.json
```

## Screenshots
<img width="2880" height="1800" alt="WhatsApp Image 2026-04-25 at 13 46 26" src="https://github.com/user-attachments/assets/462fd3b0-b51d-4785-b024-a8870fc081d0" />

<img width="2880" height="1800" alt="WhatsApp Image 2026-04-25 at 13 47 59" src="https://github.com/user-attachments/assets/9e79de19-4cfd-4b63-9e39-d2d642c4be7b" />

<img width="2880" height="1800" alt="WhatsApp Image 2026-04-25 at 13 49 08" src="https://github.com/user-attachments/assets/c09ca817-70e3-4e8a-a8a6-cd6c6a6b78d8" />





