import streamlit as st
from datetime import datetime
import base64
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment
import io

def format_timestamp(timestamp_str):
    # (Same as your original code)
    dt = datetime.fromisoformat(timestamp_str.split(".")[0])
    return dt.strftime("%B %d, %Y, %I:%M %p")

def apply_custom_css():
    # (Same as your improved CSS, but you can add more styling for new elements)
    st.markdown("""<style> ... </style>""", unsafe_allow_html=True) # Keep your CSS here

def text_to_speech_and_play(text: str):
    """Converts text to speech and returns an HTML audio player that autoplays."""
    try:
        tts = gTTS(text=text, lang='en', tld='com', slow=False)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        audio_base64 = base64.b64encode(audio_fp.read()).decode('utf-8')
        audio_tag = f'<audio autoplay="true" src="data:audio/mp3;base64,{audio_base64}">'
        st.markdown(audio_tag, unsafe_allow_html=True)
    except Exception as e:
        print(f"Error in TTS: {e}")
        st.error("Sorry, I couldn't generate voice output.")

def audio_to_text(audio_bytes):
    """Converts audio bytes to text using SpeechRecognition."""
    if not audio_bytes:
        return None
    r = sr.Recognizer()
    try:
        # Convert raw bytes to AudioData
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        # Export to a format recognizer understands (WAV)
        wav_data = io.BytesIO()
        audio_segment.export(wav_data, format="wav")
        wav_data.seek(0)
        
        with sr.AudioFile(wav_data) as source:
            audio = r.record(source)
        
        # Recognize speech
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.toast("I couldn't understand what you said. Please try again.", icon="🤔")
        return None
    except sr.RequestError as e:
        st.toast(f"Speech service error: {e}", icon="🚫")
        return None
    except Exception as e:
        st.error(f"Error processing audio: {e}")
        return None