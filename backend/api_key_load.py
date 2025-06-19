"""Load API keys from .env file."""

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
OPEN_WEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")