import streamlit as st
import os
import tempfile
import json
from groq import Groq
from elevenlabs_stt import transcribe_file
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

st.set_page_config(
    page_title="MoMento",
    page_icon="favicon.png",
    layout="wide"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f5f7fa; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    #MainMenu, footer, header { visibility: hidden; }

    .section-heading {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }
    .person-block {
        background: white;
        border-radius: 16px;
        padding: 1.5rem 1.75rem 0.75rem 1.75rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    }
    .person-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 0.5rem;
    }
    .person-avatar {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1a2f6e, #2d4aad);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1rem;
        flex-shrink: 0;
    }
    .person-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .person-summary {
        font-size: 0.88rem;
        color: #6b7280;
        margin-bottom: 1rem;
        padding-left: 54px;
    }
    .no-results {
        text-align: center;
        padding: 3rem 1rem;
        color: #9ca3af;
        font-size: 1rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    }
    .search-meta {
        font-size: 0.85rem;
        color: #9ca3af;
        margin-bottom: 1rem;
    }

    div[data-testid="stSelectbox"] label { display: none !important; }
    div[data-testid="stSelectbox"] > div { min-width: 110px !important; }

    div.stButton > button {
        background: linear-gradient(135deg, #1a2f6e, #2563eb);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        width: 100%;
    }
    div.stButton > button:hover { opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

# ── Navbar with logo image ────────────────────────────────────────────────────
st.image("logo.png", width=280)

# ── Upload & Transcribe ───────────────────────────────────────────────────────
audio_file = st.file_uploader("Upload Audio File", type=["mp3"])
st.button_clicked = st.button("Transcribe & Summarize")

if st.button_clicked:
    if audio_file is None:
        st.warning("Please upload an audio file first.")
    else:
        elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
        groq_key = os.environ.get("GROQ_API_KEY")

        if not elevenlabs_key:
            st.error("ELEVENLABS_API_KEY not found in .env file.")
        elif not groq_key:
            st.error("GROQ_API_KEY not found in .env file.")
        else:
            with st.spinner("🎙️ Transcribing audio..."):
                suffix = os.path.splitext(audio_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(audio_file.read())
                    tmp_path = tmp.name
                result = transcribe_file(tmp_path, api_key=elevenlabs_key)
                os.unlink(tmp_path)

            text = result.get("text", "")
            if not text.strip():
                st.error("Transcription returned empty text. Please try a different audio file.")
            else:
                with st.spinner("🧠 Analyzing tasks per person..."):
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
                        if raw.startswith("```"):
                            raw = raw.split("```")[1]
                            if raw.startswith("json"):
                                raw = raw[4:]
                        raw = raw.strip()
                        data = json.loads(raw)
                        st.session_state["people"] = data.get("people", [])
                        st.session_state["priorities"] = {}
                    except json.JSONDecodeError as e:
                        st.error(f"Failed to parse JSON: {e}")
                        st.code(raw, language="text")
                    except Exception as e:
                        st.error(f"Groq API error: {e}")

# ── Results ───────────────────────────────────────────────────────────────────
people = st.session_state.get("people", [])

if people:
    if "priorities" not in st.session_state:
        st.session_state["priorities"] = {}

    PRIORITY_OPTIONS = ["🔴 High", "🟡 Medium", "🟢 Low"]

    st.markdown(f'<div class="section-heading">Action Items — {len(people)} Participants</div>', unsafe_allow_html=True)

    search_query = st.text_input(
        label="",
        placeholder="🔍  Search by name or task...",
        label_visibility="collapsed"
    )

    query = search_query.strip().lower()
    filtered = [
        p for p in people
        if not query
        or query in p["name"].lower()
        or any(query in task.lower() for task in p.get("tasks", []))
    ]

    if query:
        st.markdown(
            f'<div class="search-meta">Showing {len(filtered)} of {len(people)} participants for "{search_query}"</div>',
            unsafe_allow_html=True
        )

    if not filtered:
        st.markdown(
            '<div class="no-results">😕 No participants match your search. Try a different name or keyword.</div>',
            unsafe_allow_html=True
        )
    else:
        for person in filtered:
            name = person["name"]
            summary = person.get("summary", "")
            tasks = person.get("tasks", [])

            if query and query not in name.lower():
                tasks = [t for t in tasks if query in t.lower()]

            initials = "".join([w[0].upper() for w in name.split()[:2]])

            st.markdown(f"""
            <div class="person-block">
                <div class="person-header">
                    <div class="person-avatar">{initials}</div>
                    <div class="person-name">{name}</div>
                </div>
                <div class="person-summary">{summary}</div>
            </div>
            """, unsafe_allow_html=True)

            if tasks:
                for i, task in enumerate(tasks):
                    priority_key = f"priority_{name}_{i}"
                    if priority_key not in st.session_state["priorities"]:
                        st.session_state["priorities"][priority_key] = "🟡 Medium"

                    col_task, col_priority = st.columns([5, 1])
                    with col_task:
                        st.markdown(f"""
                        <div style="background:white; border-radius:10px; padding:0.65rem 1rem;
                                    margin-bottom:6px; box-shadow:0 1px 3px rgba(0,0,0,0.06);
                                    font-size:0.92rem; color:#374151;">
                            → {task}
                        </div>
                        """, unsafe_allow_html=True)
                    with col_priority:
                        st.selectbox(
                            label="",
                            options=PRIORITY_OPTIONS,
                            index=PRIORITY_OPTIONS.index(
                                st.session_state["priorities"].get(priority_key, "🟡 Medium")
                            ),
                            key=priority_key,
                            label_visibility="collapsed"
                        )

            st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)