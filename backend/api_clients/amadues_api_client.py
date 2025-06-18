"""Amadeus API client"""

import os
from dotenv import load_dotenv
import httpx


load_dotenv()
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

class AmadeusApi:
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

amadeus = AmadeusApi()