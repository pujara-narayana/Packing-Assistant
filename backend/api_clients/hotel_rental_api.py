"""Get hotel information from Amadeus API"""

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

class AmadeusHotelAPI:
    """Amadeus API client for hotel searches"""
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

    async def search_hotels_by_city(self, city_code: str) -> list[str]:
        """
        Get a list of hotels in the visiting city

        Args:
            city_code: IATA city code (e.g., "NYC", "BOS", "LAX")

        Returns:
            List of hotel IDs
        """
        if not self.token:
            await self.get_access_token()

        url = f"{self.base_url}/v1/reference-data/locations/hotels/by-city"

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        params = {
            "cityCode": city_code,
            "radius": 15,  #kilometers
            "radiusUnit": "KM",
            "hotelSource": "ALL"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

            if response.status_code == 401:
                await self.get_access_token()
                headers["Authorization"] = f"Bearer {self.token}"
                response = await client.get(url, headers=headers, params=params)

            response.raise_for_status()
            data = response.json()

            hotel_ids = [hotel["hotelId"] for hotel in data.get("data", [])]
            return hotel_ids[:10]

    async def get_hotel_offers(self, hotel_ids: list, check_in: date, check_out: date, adults: int = 1) -> dict:
        """
        Get hotel prices

        Args:
            hotel_ids: List of hotel IDs
            check_in: Check-in date
            check_out: Check-out date
            adults: Number of adults

        Returns:
            Hotel prices
        """
        if not self.token:
            await self.get_access_token()

        url = f"{self.base_url}/v3/shopping/hotel-offers"

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        params = {
            "hotelIds": ",".join(hotel_ids),
            "checkInDate": check_in.strftime("%Y-%m-%d"),
            "checkOutDate": check_out.strftime("%Y-%m-%d"),
            "adults": adults,
            "currency": "USD",
            "roomQuantity": 1,
            "bestRateOnly": True
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

            if response.status_code == 401:
                await self.get_access_token()
                headers["Authorization"] = f"Bearer {self.token}"
                response = await client.get(url, headers=headers, params=params)

            response.raise_for_status()
            return response.json()


async def get_hotel_data_async(city_code: str, check_in: str, check_out: str, adults: int = 1) -> str:
    """
    Get hotel offers from Amadeus API asynchronously.

    Args:
        city_code: IATA city code (e.g., "NYC" for New York, "BOS" for Boston)
        check_in: Check-in date string "YYYY-MM-DD"
        check_out: Check-out date string "YYYY-MM-DD"
        adults: Number of adults (default: 1)

    Returns:
        JSON string with hotel options and prices
    """
    amadeus_hotel = AmadeusHotelAPI()
    check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

    try:
        hotel_ids = await amadeus_hotel.search_hotels_by_city(city_code)

        if not hotel_ids:
            return json.dumps({"error": "No hotels found in this city"})

        offers = await amadeus_hotel.get_hotel_offers(hotel_ids, check_in_date, check_out_date, adults)

        formatted_offers = []
        for offer in offers.get("data"):
            hotel_info = {
                "hotelId": offer.get("hotel", {}).get("hotelId"),
                "hotelName": offer.get("hotel", {}).get("name"),
                "address": offer.get("hotel", {}).get("address", {}),
                "offers": []
            }

            for hotel_offer in offer.get("offers"):
                offer_info = {
                    "id": hotel_offer.get("id"),
                    "roomType": hotel_offer.get("room", {}).get("typeEstimated", {}).get("category"),
                    "bedType": hotel_offer.get("room", {}).get("typeEstimated", {}).get("bedType"),
                    "price": hotel_offer.get("price", {}).get("total"),
                    "currency": hotel_offer.get("price", {}).get("currency"),
                    "checkInDate": hotel_offer.get("checkInDate"),
                    "checkOutDate": hotel_offer.get("checkOutDate")
                }
                hotel_info["offers"].append(offer_info)

            formatted_offers.append(hotel_info)

        return json.dumps({"hotels": formatted_offers}, indent=2)

    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_hotel_data(city_code: str, check_in: str, check_out: str, adults: int = 1) -> str:
    """Sync wrapper for the async function."""
    return asyncio.run(get_hotel_data_async(city_code, check_in, check_out, adults))