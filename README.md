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

<!-- Leave space for screenshots (add your images here) -->

### App home

![MoMento home](./screenshots/home.png)

### Action items view

![MoMento action items](./screenshots/action-items.png)
