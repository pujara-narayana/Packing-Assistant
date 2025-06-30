"""Get flight ticket information from API """

from datetime import date, datetime
import httpx
import json

from backend.api_clients.amadues_api_client import amadeus

async def search_flights(origin: str, destination: str, departure_date: date, return_date: date, adults: int = 1) -> str:
    """Search for flights with authentication

    Args:
        origin: Airport code of the current location city_to_visit.
        destination: Airport code of the destination location city_to_visit.
        departure_date: Date "YYYY-MM-DD"
        return_date: Date "YYYY-MM-DD"
        adults: Number of adults (default: 1)

    Returns:
        Weather data in JSON string format
    """
    if not amadeus.token:
        await amadeus.get_access_token()

    url = f"{amadeus.base_url}/v2/shopping/flight-offers"

    headers = {
        "Authorization": f"Bearer {amadeus.token}"
        }

    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date.strftime("%Y-%m-%d"),
        "returnDate": return_date.strftime("%Y-%m-%d"),
        "adults": adults,
        "currencyCode": "USD",
        "max": 5
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)

        if response.status_code == 401:
            await amadeus.get_access_token()
            headers["Authorization"] = f"Bearer {amadeus.token}"
            response = await client.get(url, headers=headers, params=params)

        response.raise_for_status()
        return response.json()

async def get_flight_data_async(origin: str, destination: str, departure_date: str, return_date: str, adults: int = 1) -> str:
    """
    Get flight offers from Amadeus API asynchronously.

    Args:
        origin: Airport code of the current location city_to_visit.
        destination: Airport code of the destination location city_to_visit.
        departure_date: Date string "YYYY-MM-DD"
        return_date: Date string "YYYY-MM-DD"
        adults: Number of adults (default: 1)

    Returns:
        Weather data in JSON string format, or raise an exception if an error occurs.
    """
    departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
    return_date = datetime.strptime(return_date, "%Y-%m-%d").date()

    try:
        data = await search_flights(origin, destination, departure_date, return_date, adults)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"