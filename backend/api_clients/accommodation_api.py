"""Get accommodation data from the API."""

import asyncio
import httpx
import json
from langchain.tools import tool

from backend.api_clients.travel_search_api import get_place_id_of_city
from backend.api_key_load import GEOAPIFY_API_KEY


async def get_accommodation_data(city_full_info: str) -> str:
    """Get accommodation data from the API.

    Args:
        city_full_info (str): The city_to_visit name with state and country.

    Returns:
        json_data (str): JSON string with accommodation data but won't give prices of the accommodation.
        """
    place_id = await get_place_id_of_city(city_full_info)
    get_accommodation_url = f"https://api.geoapify.com/v2/places?categories=accommodation.motel,accommodation,accommodation.hotel,accommodation.guest_house,accommodation.hostel&filter=place:{place_id}&limit=10&apiKey={GEOAPIFY_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(get_accommodation_url)
        response.raise_for_status()
        travel_data = response.json()
        return json.dumps(travel_data, indent=2)

@tool
def get_accommodation_data_of_city(city: str) -> str:
    """Sync wrapper for the async function."""
    return asyncio.run(get_accommodation_data(city))