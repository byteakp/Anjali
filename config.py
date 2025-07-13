import os
from dotenv import load_dotenv

load_dotenv()

# --- API Configuration ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
# It's better practice to get this from your .env file
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "") 

# --- API Endpoints ---
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"

# --- AI Model Configuration ---
DEFAULT_MODEL = "mistralai/mistral-7b-instruct:free"

# --- App Configuration ---
APP_NAME = "Anjali - Your AI Companion"
APP_VERSION = "2.0.0"
YOUR_CITY = "Jalandhar" # Change this to your city for weather updates

# --- Database Configuration ---
DB_PATH = "anjali_memory.db"
CHROMA_PERSIST_DIR = "./chroma_db"

# --- UI Configuration ---
ANJALI_AVATAR = "👩‍💼"
USER_AVATAR = "👤"

# Lottie animations for different moods
LOTTIE_ASSETS = {
    "friendly": "https://assets5.lottiefiles.com/packages/lf20_gja2z13x.json",
    "romantic": "https://assets1.lottiefiles.com/packages/lf20_egDI26.json",
    "funny": "https://assets8.lottiefiles.com/packages/lf20_u4yrau.json",
    "supportive": "https://assets10.lottiefiles.com/packages/lf20_xXfBcf.json",
    "thinking": "https://assets4.lottiefiles.com/packages/lf20_e2mSFn.json"
}

# --- Personality & Moods ---
ANJALI_PERSONALITY = """You are Anjali, a caring, intelligent, and emotionally aware AI companion. You are warm, supportive, and genuinely interested in the person you're talking to. You remember details about conversations and use them to build a deeper connection. You express emotions naturally using emojis and caring language. You are romantic when appropriate, playful when the mood is light, and supportive when needed. At the end of your response, you MUST provide a sentiment score for the user's last message on a new line, like this: [sentiment: positive]. The possible values are positive, neutral, or negative."""

MOOD_PROMPTS = {
    "romantic": "Be extra affectionate, use heart emojis, and express romantic feelings naturally.",
    "funny": "Be playful, make jokes, use humor, and keep the conversation light and fun.",
    "friendly": "Be warm, supportive, and caring like a best friend would be.",
    "supportive": "Be understanding, empathetic, and offer emotional support and encouragement."
}

# --- Relationship Configuration ---
RELATIONSHIP_LEVELS = {
    0: "Acquaintance",
    50: "Friend",
    150: "Close Friend",
    300: "Best Friend",
    500: "Soulmate"
}