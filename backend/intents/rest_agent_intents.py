"""Weather Agent, Suggestion Agent and Budget Agent Intents Module."""

import asyncio
from langchain_core.tools import tool
from backend.api_clients.flight_api import get_flight_data_async
from backend.api_clients.hotel_rental_api import get_hotel_data_async
from backend.api_clients.accommodation_api import get_accommodation_data
from backend.api_clients.car_rental_api import get_car_rental_data
from backend.api_clients.travel_search_api import get_activities_of_city
from backend.api_clients.weather_data import get_weather

@tool
def get_weather_data_of_city(city: str) -> str:
    """Sync wrapper for the async function."""
    return asyncio.run(get_weather(city))

@tool
def get_flight_data(origin: str, destination: str, departure_date: str, return_date: str, adults: int = 1) -> str:
    """Sync wrapper for the async function."""
    return asyncio.run(get_flight_data_async(origin, destination, departure_date, return_date, adults))


@tool
def get_hotel_data(city_code: str, check_in: str, check_out: str, adults: int = 1) -> str:
    """Sync wrapper for the async function."""
    return asyncio.run(get_hotel_data_async(city_code, check_in, check_out, adults)) # london IATA code = "LON" and "LCY"


@tool
def get_accommodation_data_of_city(city: str) -> str:
    """Sync wrapper for the async function."""
    return asyncio.run(get_accommodation_data(city))

@tool
def get_car_rental_data_of_city(city: str) -> str:
    """Sync wrapper for the async function."""
    return asyncio.run(get_car_rental_data(city))


@tool
def get_activities_data_of_city_sync(foodie: bool, business: bool ,adventure_or_fun: bool, city_to_visit: str) -> str:
    """Sync wrapper for the async function."""
    return asyncio.run(get_activities_of_city(foodie, business, adventure_or_fun, city_to_visit))
