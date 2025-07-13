import requests
import json
import re
from typing import List, Dict
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from config import (OPENROUTER_API_KEY, OPENROUTER_BASE_URL, DEFAULT_MODEL,
                    ANJALI_PERSONALITY, MOOD_PROMPTS, WEATHER_API_KEY, 
                    WEATHER_API_URL, YOUR_CITY)

class ChatModel:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.model = DEFAULT_MODEL

    def generate_response(self, messages: List[Dict], mood: str = "friendly", temperature: float = 0.8) -> (str, str):
        system_message = ANJALI_PERSONALITY
        if mood in MOOD_PROMPTS:
            system_message += f"\n\n{MOOD_PROMPTS[mood]}"

        full_messages = [{"role": "system", "content": system_message}] + messages
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {"model": self.model, "messages": full_messages, "temperature": temperature, "max_tokens": 500}

        try:
            response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            result = response.json()['choices'][0]['message']['content']
            
            # Extract content and sentiment
            sentiment_match = re.search(r"\[sentiment: (positive|neutral|negative)\]", result)
            sentiment = "neutral"
            if sentiment_match:
                sentiment = sentiment_match.group(1)
                # Remove the sentiment tag from the response shown to the user
                content = re.sub(r"\[sentiment: (positive|neutral|negative)\]", "", result).strip()
            else:
                content = result

            return content, sentiment
        except Exception as e:
            print(f"Error calling OpenRouter: {e}")
            return "I'm having a little trouble connecting right now. Let's try again in a moment. 💭", "neutral"

class ImageCaptionModel:
    # (This class remains the same as your original code)
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = None
        self.model = None
        self.model_loaded = False
    def load_model(self):
        if not self.model_loaded:
            try:
                self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
                self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
                self.model.to(self.device)
                self.model_loaded = True
            except Exception as e:
                print(f"Error loading BLIP model: {e}")
    def caption_image(self, image: Image.Image) -> str:
        if not self.model_loaded: self.load_model()
        if not self.model_loaded: return "I can see you've shared an image with me! 📸"
        try:
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            out = self.model.generate(**inputs, max_length=50)
            return self.processor.decode(out[0], skip_special_tokens=True)
        except Exception: return "I can see you've shared a lovely image! 🖼️"

class MemoryProcessor:
    # (This class remains the same as your original code)
    def __init__(self, db):
        self.db = db
    def extract_important_info(self, text: str) -> List[Dict]:
        memories = []
        lower_text = text.lower()
        if "my name is" in lower_text or "i'm" in lower_text or "i am" in lower_text:
            memories.append({"type": "personal_info", "content": text, "importance": 8})
        if any(w in lower_text for w in ["favorite", "love", "like", "prefer"]):
            memories.append({"type": "preference", "content": text, "importance": 6})
        if any(w in lower_text for w in ["birthday", "anniversary", "tomorrow", "yesterday", "meeting"]):
            memories.append({"type": "event", "content": text, "importance": 7})
        if any(w in lower_text for w in ["happy", "sad", "excited", "worried", "stressed"]):
            memories.append({"type": "emotion", "content": text, "importance": 5})
        return memories
    def get_relevant_context(self, query: str, limit: int = 3) -> str:
        results = self.db.search_memories(query, n_results=limit)
        if results and results['documents']:
            context = "Here's what I remember:\n" + "\n".join([f"- {doc}" for doc in results['documents'][0]])
            return context
        return ""

class DailyBriefingModel:
    def get_weather(self):
        if not WEATHER_API_KEY or not YOUR_CITY:
            return "Weather information isn't set up."
        try:
            params = {"key": WEATHER_API_KEY, "q": YOUR_CITY, "aqi": "no"}
            response = requests.get(WEATHER_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return (f"The weather in {YOUR_CITY} is currently {data['current']['temp_c']}°C "
                    f"and feels like {data['current']['condition']['text']}.")
        except Exception as e:
            return "Sorry, I couldn't fetch the weather right now."

    def get_quote_of_the_day(self):
        try:
            response = requests.get("https://zenquotes.io/api/random")
            response.raise_for_status()
            data = response.json()[0]
            return f'Quote of the day: "{data["q"]}" - {data["a"]}'
        except Exception:
            return "Let's make today a great day!"

    def generate_briefing(self):
        weather = self.get_weather()
        quote = self.get_quote_of_the_day()
        return f"Good morning! Here's your daily briefing:\n\n- **Weather**: {weather}\n- **Inspiration**: {quote}"