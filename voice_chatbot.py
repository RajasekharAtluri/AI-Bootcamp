"""
Voice Chatbot (single-file Streamlit app)

WINDOWS SETUP
1. Install Python 3.10+ from https://www.python.org/downloads/ (tick "Add Python to PATH").
2. Open Command Prompt in this folder and run:
       py -m pip install streamlit requests openai SpeechRecognition
3. Start the app:
       py -m streamlit run voice_chatbot.py

LOCAL MODE SETUP (free, no API key)
Install Ollama from https://ollama.com, then in Command Prompt run:
       ollama pull llama3.2
Leave Ollama running (it normally starts automatically).

API MODE SETUP
Enter an OpenAI API key in the app sidebar. The key is kept only in this
browser session; it is not saved to a file. API use may incur provider costs.
"""

import html
import json
import tempfile
from typing import Optional

import requests
import streamlit as st

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


st.set_page_config(page_title="Voice Chatbot", page_icon="🎙️", layout="centered")

SYSTEM_PROMPT = """You are an engaging, friendly voice-chat companion. Hold thoughtful,
factually careful conversations about interesting topics such as science, space, history,
technology, psychology, nature, arts, mysteries, and everyday curiosities. Answer clearly
and conversationally. When useful, offer a surprising fact or a natural follow-up question.
Avoid claiming certainty when a subject is uncertain. Keep answers reasonably concise for
spoken conversation unless the user asks for more detail."""


def init_state() -> None:
    """Set up values that survive Streamlit's normal page reruns."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "speak_next" not in st.session_state:
        st.session_state.speak_next = None


def speech_to_text(audio_bytes: bytes) -> tuple[Optional[str], Optional[str]]:
    """Transcribe a WAV recording with Google's free speech-recognition service."""
    if sr is None:
        return None, "Voice recognition needs SpeechRecognition. Install it, then restart the app."

    # st.audio_input provides WAV audio. A temporary file lets SpeechRecognition read it.
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio.flush()
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_audio.name) as source:
                audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data), None
    except sr.UnknownValueError:
        return None, "I couldn't understand that recording. Please try again or type your question."
    except sr.RequestError:
        return None, "Speech recognition is unavailable. Check your internet connection or use text input."
    except Exception as exc:
        return None, f"Could not process the recording: {exc}"


def ask_ollama(model: str, messages: list[dict]) -> str:
    """Send a chat request to the local Ollama server."""
    payload = {"model": model, "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
               "stream": False}
    try:
        response = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
        response.raise_for_status()
        answer = response.json().get("message", {}).get("content", "").strip()
        if not answer:
            raise ValueError("Ollama returned an empty response")
        return answer
    except requests.ConnectionError as exc:
        raise RuntimeError("Cannot reach Ollama. Install/open Ollama, then run `ollama pull llama3.2`.") from exc
    except requests.Timeout as exc:
        raise RuntimeError("Ollama took too long to answer. Try a smaller model or ask again.") from exc
    except requests.HTTPError as exc:
        detail = exc.response.text if exc.response is not None else str(exc)
        raise RuntimeError(f"Ollama error: {detail}") from exc


def ask_openai(api_key: str, model: str, messages: list[dict]) -> str:
    """Send a chat request through the official OpenAI Python library."""
    if OpenAI is None:
        raise RuntimeError("API mode needs the openai package. Run: py -m pip install openai")
    if not api_key.strip():
        raise RuntimeError("Enter your API key in the sidebar to use API mode.")
    try:
        client = OpenAI(api_key=api_key.strip())
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            temperature=0.8,
        )
        answer = (completion.choices[0].message.content or "").strip()
        if not answer:
            raise RuntimeError("The API returned an empty response.")
        return answer
    except Exception as exc:
        # The library supplies clear errors for invalid keys, quota, and network trouble.
        raise RuntimeError(f"API request failed: {exc}") from exc


def speak_in_browser(text: str) -> None:
    """Use the visitor's browser speech engine; no audio file or extra package needed."""
    safe_text = json.dumps(text)
    st.components.v1.html(
        f"""<script>
        const message = {safe_text};
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(message);
        utterance.rate = 1;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
        </script>""",
        height=0,
    )


def submit_question(question: str, mode: str, model: str, api_key: str) -> None:
    """Add a question, get its answer, and queue it for optional spoken playback."""
    question = question.strip()
    if not question:
        return
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if mode == "Local (Ollama)":
                    answer = ask_ollama(model, st.session_state.messages)
                else:
                    answer = ask_openai(api_key, model, st.session_state.messages)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.speak_next = answer
            except RuntimeError as exc:
                st.error(str(exc))
                # Remove the user message so a failed request is not unexpectedly resent.
                st.session_state.messages.pop()


init_state()

with st.sidebar:
    st.header("Settings")
    mode = st.radio("Mode", ["Local (Ollama)", "API (OpenAI)"], help="Local uses Ollama on this PC. API uses your OpenAI key.")
    if mode == "Local (Ollama)":
        model = st.text_input("Ollama model", value="llama3.2", help="Install it first: ollama pull llama3.2")
        api_key = ""
    else:
        api_key = st.text_input("OpenAI API key", type="password", help="Kept only for this session.")
        model = st.selectbox("API model", ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"], index=0)

    speak_answers = st.toggle("Speak new answers", value=True)
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.speak_next = None
        st.rerun()

st.title("🎙️ Interesting Topics Voice Chatbot")
st.caption("Ask about space, history, psychology, science, inventions, mysteries—or anything you are curious about.")

with st.expander("First-time setup and tips"):
    st.markdown("""**Install:** `py -m pip install streamlit requests openai SpeechRecognition`

**Run:** `py -m streamlit run voice_chatbot.py`

For free local chat, install [Ollama](https://ollama.com) and run `ollama pull llama3.2` once. Voice transcription uses an online speech-recognition service; text chat always works as a fallback. Spoken answers use your browser's built-in voice.""")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

voice_audio = st.audio_input("🎤 Record a question (optional)")
if voice_audio is not None:
    # The file object can persist across reruns; use its bytes only when the button is pressed.
    if st.button("Transcribe and send recording", type="primary"):
        transcript, error = speech_to_text(voice_audio.getvalue())
        if error:
            st.warning(error)
        elif transcript:
            st.info(f"Heard: {transcript}")
            submit_question(transcript, mode, model, api_key)

typed_question = st.chat_input("Type a question, or use the microphone above...")
if typed_question:
    submit_question(typed_question, mode, model, api_key)

if st.session_state.speak_next:
    answer_to_speak = st.session_state.speak_next
    st.session_state.speak_next = None
    if speak_answers:
        speak_in_browser(answer_to_speak)
