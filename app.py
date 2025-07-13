import streamlit as st
from streamlit_lottie import st_lottie
import requests
import io
from PIL import Image

# Import project modules
from config import (
    APP_NAME, ANJALI_AVATAR, USER_AVATAR, LOTTIE_ASSETS
)
from database import MemoryDatabase
from ai_models import ChatModel, ImageCaptionModel, MemoryProcessor, DailyBriefingModel
from utils import apply_custom_css, text_to_speech_and_play, audio_to_text

# --- INITIALIZATION ---
def init_session_state():
    """Initialize Streamlit session state variables."""
    if "db" not in st.session_state:
        st.session_state.db = MemoryDatabase()
    if "chat_model" not in st.session_state:
        st.session_state.chat_model = ChatModel()
    if "image_model" not in st.session_state:
        st.session_state.image_model = ImageCaptionModel()
    if "memory_processor" not in st.session_state:
        st.session_state.memory_processor = MemoryProcessor(st.session_state.db)
    if "briefing_model" not in st.session_state:
        st.session_state.briefing_model = DailyBriefingModel()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mood" not in st.session_state:
        st.session_state.mood = "friendly"
    if "speak_output" not in st.session_state:
        st.session_state.speak_output = False
    # Initialize a key for the chat input to handle programmatic updates
    if "last_prompt" not in st.session_state:
        st.session_state.last_prompt = ""


# --- UI COMPONENTS ---
def display_header():
    """Displays the main header with Lottie animation and relationship status."""
    rel_status = st.session_state.db.get_relationship_status()
    level = rel_status.get('level', 'Acquaintance')
    points = rel_status.get('points', 0)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        lottie_url = LOTTIE_ASSETS.get(st.session_state.mood, LOTTIE_ASSETS["friendly"])
        try:
            # Safely get the Lottie animation with a timeout
            response = requests.get(lottie_url, timeout=10)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            lottie_json = response.json()
            st_lottie(lottie_json, speed=1, height=150, key="lottie_mood")
        except (requests.exceptions.RequestException, requests.exceptions.JSONDecodeError) as e:
            # If the request fails or the response isn't valid JSON, show a placeholder emoji
            st.markdown(f"<h1 style='font-size: 100px; text-align: center;'>{ANJALI_AVATAR}</h1>", unsafe_allow_html=True)
            print(f"Error: Could not load Lottie animation from {lottie_url}. Reason: {e}")

    with col2:
        st.title(APP_NAME)
        # Ensure points are within 0-100 for the progress bar
        progress_value = points % 100 if points < 500 else 100
        st.progress(progress_value, text=f"**Relationship Level: {level}** ({points} points)")
        st.write(f"Her current mood is: **{st.session_state.mood.capitalize()}**")


def setup_sidebar():
    """Configures and displays the sidebar elements."""
    with st.sidebar:
        st.header("Controls")
        st.session_state.speak_output = st.toggle("Speak Responses", value=False, help="Enable to hear Anjali's responses.")
        
        st.header("Actions")
        if st.button("☀️ Daily Briefing", use_container_width=True):
            briefing = st.session_state.briefing_model.generate_briefing()
            add_message("assistant", briefing, display_now=True)
        
        st.header("Record Voice Message")
        audio_bytes = st.audio_recorder(text="Click to record", icon="🎤")
        if audio_bytes:
            with st.spinner("Transcribing your voice..."):
                transcript = audio_to_text(audio_bytes)
                if transcript:
                    # Use a session state variable to set the chat input value
                    st.session_state.last_prompt = transcript
                    st.rerun()

        st.header("Share an Image")
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file


# --- CORE LOGIC ---
def add_message(role, content, display_now=False):
    """Adds a message to the chat history and saves it to the database."""
    st.session_state.messages.append({"role": role, "content": content})
    st.session_state.db.save_conversation(role=role, content=content, mood=st.session_state.mood)
    if display_now:
        with st.chat_message(role, avatar=ANJALI_AVATAR if role == "assistant" else USER_AVATAR):
            st.write(content)
        if role == "assistant" and st.session_state.speak_output:
            text_to_speech_and_play(content)

def process_user_input(prompt):
    """Handles user input, generates AI response, and updates the state."""
    if not prompt and "uploaded_file" not in st.session_state:
        st.warning("Please enter a message or upload a file.")
        return
        
    add_message("user", prompt)

    image_context = ""
    uploaded_file = st.session_state.pop("uploaded_file", None) # Use pop to consume the file

    with st.chat_message("user", avatar=USER_AVATAR):
        if uploaded_file:
            st.image(uploaded_file, width=200)
        st.write(prompt)

    if uploaded_file:
        with st.spinner("Looking at the image..."):
            image = Image.open(uploaded_file).convert("RGB")
            caption = st.session_state.image_model.caption_image(image)
            image_context = f"\nThe user has shared an image with me. I see: {caption}"

    with st.spinner("Anjali is thinking..."):
        context = st.session_state.memory_processor.get_relevant_context(prompt)
        
        # Construct messages for the model
        model_messages = st.session_state.messages[-10:] # Get recent history
        if context:
            model_messages.insert(0, {"role": "system", "content": context})
        if image_context:
            model_messages[-1]["content"] += image_context # Add image context to the last user message
        
        response, sentiment = st.session_state.chat_model.generate_response(
            model_messages,
            mood=st.session_state.mood
        )
        
        # Update relationship based on sentiment
        st.session_state.db.update_interaction_metrics(sentiment)
        
        # Process and save new memories from both user prompt and AI response
        for text_to_process, text_context in [(prompt, "User said"), (response, "Anjali said")]:
            memories = st.session_state.memory_processor.extract_important_info(text_to_process)
            for mem in memories:
                st.session_state.db.save_memory(mem["content"], mem["type"], mem["importance"], context=text_context)
    
    add_message("assistant", response, display_now=True)

# --- MAIN APP ---
def main():
    st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="👩‍💼")
    apply_custom_css()
    init_session_state()

    display_header()
    setup_sidebar()

    # Display chat history from session state
    for message in st.session_state.messages:
        avatar = ANJALI_AVATAR if message["role"] == "assistant" else USER_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])

    # Use the session state variable as the value for the chat_input
    prompt = st.chat_input("What's on your mind?", key="chat_input_main")
    
    # If the voice-to-text has populated our variable, use it
    if st.session_state.last_prompt:
        prompt = st.session_state.last_prompt
        st.session_state.last_prompt = "" # Clear it after use

    if prompt:
        process_user_input(prompt)
        st.rerun()

if __name__ == "__main__":
    main()
