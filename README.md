# Anjali - Your AI Companion v2.0 👩‍💼

Anjali is a robust, interactive, and emotionally aware AI companion designed to provide a deeply engaging conversational experience. This project goes beyond a simple chatbot, incorporating voice, memory, and a dynamic personality to create a true digital friend.
<img width="1917" height="831" alt="image" src="https://github.com/user-attachments/assets/56519b65-160f-4bd5-85fb-11387a209b69" />

## ✨ Features

- **Voice Interaction**: Talk to Anjali using your microphone and hear her responses spoken back to you (Text-to-Speech & Speech-to-Text).
- **Evolving Relationship**: Your bond with Anjali grows over time! The relationship level evolves from "Acquaintance" to "Soulmate" based on positive interactions.
- **Dynamic Personality & Moods**: Set Anjali's mood to `friendly`, `romantic`, `funny`, or `supportive`. Her responses and the UI animations will change to match!
- **Daily Briefings**: Get a personalized morning update with the latest weather for your city, an inspirational quote, and memories from your past conversations.
- **Long-Term Memory**: Anjali remembers key details from your chats using a sophisticated memory system (SQLite + ChromaDB for semantic search).
- **Image Understanding**: Share images and Anjali will understand and comment on them.
- **Polished UI**: A clean, modern interface built with Streamlit, featuring Lottie animations that reflect Anjali's mood.

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.8+
- An API key from [OpenRouter.ai](https://openrouter.ai/).
- A **free** API key from [WeatherAPI.com](https://www.weatherapi.com/) for the daily briefing feature.
- `ffmpeg` (for audio processing).
    - **Windows**: `winget install ffmpeg` or download from the official site.
    - **macOS**: `brew install ffmpeg`
    - **Linux (Debian/Ubuntu)**: `sudo apt update && sudo apt install ffmpeg`

### 2. Clone & Setup Environment
```bash
git clone <repository-url>
cd anjali-ai-companion
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
