"""Get data from the Travel Search API"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")


async def get_place_id_of_city(full_city_to_visit_info: str) -> str | None:
    """
    Fetches place ID of a city from GeoAPIfy API asynchronously.

    Args:
        full_city_to_visit_info (str): The city_to_visit name with state and country.

    Returns:
        place_id (str): Place ID of the city.
    """
    full_city_to_visit_info = full_city_to_visit_info.replace(" ", "%20")
    search_place_id_url = f"https://api.geoapify.com/v1/geocode/search?text=38%20{full_city_to_visit_info}&apiKey={GEOAPIFY_API_KEY}"

    async with httpx.AsyncClient() as client:
        response = await client.get(search_place_id_url)
        response.raise_for_status()
        data = response.json()
        return data["features"][0]["properties"]["place_id"]


async def get_activities_of_city(foodie: bool, adventure_or_fun: bool, business: bool, city_to_visit: str) -> str | None:
    """
    Fetches the activities to in a city from GeoAPIfy API asynchronously.

    Args:
        foodie (bool): Whether the user is a foodie.
        adventure_or_fun (bool): Whether the user wants to do adventure or fun.
        business (bool): Whether the user wants to relax or enjoy nature.
        city_to_visit (str): The city_to_visit name with state and country.

    Returns:
        json_data (str): JSON string with activities data.
    """

    place_id = await get_place_id_of_city(city_to_visit)

    get_activities_url = ""
    if foodie:
        get_activities_url = f"https://api.geoapify.com/v2/places?categories=catering.restaurant,catering.cafe&filter=place:{place_id}&limit=10&apiKey={GEOAPIFY_API_KEY}"

    if business:

        get_activities_url = f"https://api.geoapify.com/v2/places?categories=leisure,natural,tourism,heritage,beach&filter=place:{place_id}&limit=10&apiKey={GEOAPIFY_API_KEY}"

    if adventure_or_fun:

        get_activities_url = f"https://api.geoapify.com/v2/places?categories=entertainment,entertainment.theme_park,entertainment.water_park&filter=place:{place_id}&limit=10&apiKey={GEOAPIFY_API_KEY}"

    async with httpx.AsyncClient() as client:

        response = await client.get(get_activities_url)
        response.raise_for_status()
        travel_data = response.json()
        return json.dumps(travel_data, indent=2)


@tool
def get_activities_data_of_city_sync(foodie: bool, adventure_or_fun: bool, relax_nature: bool, city_to_visit: str) -> str:
    """Sync wrapper for the async function."""
    return asyncio.run(get_activities_of_city(foodie, adventure_or_fun, relax_nature, city_to_visit))