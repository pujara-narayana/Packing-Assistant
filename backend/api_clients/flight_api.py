"""Get flight ticket information from API """

from datetime import date, datetime
import asyncio
import os
from dotenv import load_dotenv
import httpx
import json

from langchain.tools import tool

load_dotenv()
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

class AmadeusAPI:
    """Amadeus API client"""
    def __init__(self):
        self.api_key = AMADEUS_API_KEY
        self.api_secret = AMADEUS_API_SECRET
        self.token = None
        self.base_url = "https://test.api.amadeus.com"

    async def get_access_token(self):
        """Get OAuth2 access token"""
        token_url = f"{self.base_url}/v1/security/oauth2/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                return self.token
            else:
                raise Exception(f"Failed to get token: {response.text}")

    async def search_flights(self, origin: str, destination: str, departure_date: date, return_date: date) -> str:
        """Search for flights with authentication

        Args:
            origin: Airport code of the current location city_to_visit.
            destination: Airport code of the destination location city_to_visit.
            departure_date: Date "YYYY-MM-DD"
            return_date: Date "YYYY-MM-DD"

        Returns:
            Weather data in JSON string format
        """
        if not self.token:
            await self.get_access_token()

        url = f"{self.base_url}/v2/shopping/flight-offers"

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date.strftime("%Y-%m-%d"),
            "returnDate": return_date.strftime("%Y-%m-%d"),
            "adults": 1,
            "currencyCode": "USD",
            "max": 5
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

            if response.status_code == 401:
                await self.get_access_token()
                headers["Authorization"] = f"Bearer {self.token}"
                response = await client.get(url, headers=headers, params=params)

            response.raise_for_status()
            return response.json()


async def get_flight_data_async(origin: str, destination: str, departure_date: str, return_date: str) -> str:
    """
    Get flight offers from Amadeus API asynchronously.

    Args:
        origin: Airport code of the current location city_to_visit.
        destination: Airport code of the destination location city_to_visit.
        departure_date: Date string "YYYY-MM-DD"
        return_date: Date string "YYYY-MM-DD"

    Returns:
        Weather data in JSON string format, or raise an exception if an error occurs.
    """
    amadeus = AmadeusAPI()
    departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
    return_date = datetime.strptime(return_date, "%Y-%m-%d").date()

    try:
        data = await amadeus.search_flights(origin, destination, departure_date, return_date)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_flight_data(origin: str, destination: str, departure_date: str, return_date: str) -> str:
    """Sync wrapper for the async function."""
    return asyncio.run(get_flight_data_async(origin, destination, departure_date, return_date))