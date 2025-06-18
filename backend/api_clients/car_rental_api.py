"""Get car rental data"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv
from langchain.tools import tool

from backend.api_clients.travel_search_api import get_place_id_of_city

load_dotenv()
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

async def get_car_rental_data(city_to_visit: str) -> str:
    """Get car rental data from the API.

    Args:
        city_to_visit (str): The city_to_visit name with state and country.

    Returns:
        json_data (str): JSON string with car rental data but won't give prices of the car rental.
        """

    place_id = await get_place_id_of_city(city_to_visit)
    get_car_rental_url = f"https://api.geoapify.com/v2/places?categories=rental.car&filter=place:{place_id}&limit=10&apiKey={GEOAPIFY_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(get_car_rental_url)
        response.raise_for_status()
        travel_data = response.json()
        return json.dumps(travel_data, indent=2)

@tool
def get_car_rental_data_of_city(city: str) -> str:
    """Sync wrapper for the async function."""
    return asyncio.run(get_car_rental_data(city))