# Configuration and API keys

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# ---------------------------
# ✅ Groq LLM Configuration
# ---------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"  # Default Groq endpoint
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
LLAMA3_MODEL = "llama3-8b-8192"  # You can switch to another if needed

# ---------------------------
# 🌍 Weather API (optional)
# ---------------------------
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# ---------------------------
# 🏙️ Google Places API (optional)
# ---------------------------
GEOAPIFY_PLACES_API_KEY = os.getenv("GEOAPIFY_PLACES_API_KEY")

# ---------------------------
# ✈️ Flights / Hotels API (if any 3rd party or mock)
# ---------------------------
FLIGHT_API_KEY = os.getenv("FLIGHT_API_KEY")
HOTEL_API_KEY = os.getenv("HOTEL_API_KEY")

# ---------------------------
# 🌍 Project Defaults
# ---------------------------
DEFAULT_CITY = "Dubai"
DEFAULT_COUNTRY = "UAE"
DEFAULT_CURRENCY = "AED"

# ---------------------------
# 🧠 Embeddings Model
# ---------------------------
EMBEDDINGS_MODEL = "all-MiniLM-L6-v2"  # SentenceTransformers

