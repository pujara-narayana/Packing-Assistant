"""Get car rental data"""

import httpx
import json

from backend.api_clients.travel_search_api import get_place_id_of_city
from backend.api_key_load import GEOAPIFY_API_KEY


async def get_car_rental_data(city_to_visit: str) -> str:
    """Get car rental data from the API.

    Args:
        city_to_visit (str): The city_to_visit name with state and country.

    Returns:
        json_data (str): JSON string with car rental data but won't give prices of the car rental.
        """

    place_id = await get_place_id_of_city(city_to_visit)
    get_car_rental_url = f"https://api.geoapify.com/v2/places?categories=rental.car&filter=place:{place_id}&limit=5&apiKey={GEOAPIFY_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(get_car_rental_url)
        response.raise_for_status()
        travel_data = response.json()
        return json.dumps(travel_data, indent=2)