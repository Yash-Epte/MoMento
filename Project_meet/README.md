# ElevenLabs Speech-to-Text (audio → text)

## Setup

```bash
cd "Project_meet"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (this is ignored by git):

```bash
cp .env.example .env
# then edit .env and set ELEVENLABS_API_KEY=...
```

## Run

```bash
python3 elevenlabs_stt.py ./audio.mp3
python3 elevenlabs_stt.py ./audio.wav --diarize --language-code en --out-json transcript.json
```
