"""Get necessary information regarding the weather."""

import asyncio
import httpx
import json
from langchain.tools import tool

from backend.api_key_load import OPEN_WEATHER_KEY

async def get_weather(city_to_visit: str) -> str | None:
    """
    Fetches weather data from OpenWeatherMap API asynchronously.

    Args:
        city_to_visit (str): The city_to_visit name.

    Returns:
        Weather data in JSON string format, or None if an error occurs.
    """
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city_to_visit, "appid": OPEN_WEATHER_KEY, "units": "metric"}

    async with httpx.AsyncClient() as client:

        try:
          response = await client.get(base_url, params=params)
          response.raise_for_status()
          weather_data = response.json()
          return json.dumps(weather_data, indent=2)

        except httpx.HTTPError as e:
            print(f"HTTP Error: {e}")
            return None

@tool
def get_weather_data_of_city(city: str) -> str:
    """Sync wrapper for the async function."""
    return asyncio.run(get_weather(city))