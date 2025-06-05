import http.client
import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from src.configuration import HOTEL_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class HotelSearchParams:
    city: str
    checkin_date: str  # Format: "YYYY-MM-DD"
    checkout_date: str  # Format: "YYYY-MM-DD"
    adults: int = 2
    currency: str = "USD"
    locale: str = "en-us"


class HotelAPIClient:
    def __init__(
            self,
            api_key: Optional[str] = None,
            api_host: str = "agoda-com.p.rapidapi.com",
            base_endpoint: str = "/hotels",
    ):
        """
        Initialize the Hotel API client.
        """
        self.api_key = HOTEL_API_KEY or api_key
        if not self.api_key:
            raise ValueError("Hotel API key not provided and HOTEL_API_KEY env var not set")

        self.api_host = api_host
        self.base_endpoint = base_endpoint
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': self.api_host,
            'Content-Type': 'application/json',
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        conn = http.client.HTTPSConnection(self.api_host)
        query_str = f"?{'&'.join([f'{k}={v}' for k, v in params.items()])}" if params else ""
        full_url = f"{self.base_endpoint}{endpoint}{query_str}"

        try:
            logger.info(f"Requesting {method} {full_url}")
            conn.request(method, full_url, headers=self.headers)
            response = conn.getresponse()
            data = response.read().decode("utf-8")

            if response.status != 200:
                raise ValueError(f"API Error {response.status}: {data}")

            return json.loads(data)
        finally:
            conn.close()

    def search_hotels(self, params: HotelSearchParams) -> Dict:
        """
        Search for hotels in a city with check-in/check-out dates.
        """
        # Step 1: Get city ID from auto-complete
        autocomplete_params = {"query": params.city}
        autocomplete_data = self._make_request("GET", "/auto-complete", autocomplete_params)

        if not autocomplete_data:
            raise ValueError(f"No results found for city: {params.city}")

        # Return the raw autocomplete data for inspection
        return autocomplete_data

    def get_hotels(self, params: HotelSearchParams) -> Dict:
        """
        Get detailed hotel information including prices
        """
        # First get the autocomplete results
        autocomplete_data = self.search_hotels(params)

        if not isinstance(autocomplete_data, dict) or not autocomplete_data.get("data"):
            raise ValueError(f"Invalid response format for city: {params.city}")

        # Take the first result (you might want to handle multiple results differently)
        first_hotel = autocomplete_data["data"][0] if autocomplete_data["data"] else None
        if not first_hotel:
            raise ValueError(f"No hotel data available for city: {params.city}")

        hotel_id = first_hotel.get("id")
        if not hotel_id:
            raise ValueError("Hotel ID not found in response")

        # Get detailed hotel info
        search_params = {
            "id": hotel_id,
            "checkinDate": params.checkin_date,
            "checkoutDate": params.checkout_date,
            "adults": params.adults,
            "currency": params.currency,
            "locale": params.locale
        }

        hotel_data = self._make_request("GET", "/search-overnight", search_params)

        return {
            "city": params.city,
            "checkin_date": params.checkin_date,
            "checkout_date": params.checkout_date,
            "hotel_info": hotel_data['data']['searchResult']
        }


if __name__ == "__main__":
    client = HotelAPIClient()

    hotel_params = HotelSearchParams(
        city="Paris",
        checkin_date="2025-06-03",
        checkout_date="2025-06-12",
        adults=2,
        currency="EUR"
    )

    try:
        autocomplete_results = client.search_hotels(hotel_params)
        print("Autocomplete Results:")


      #  print(json.dumps(autocomplete_results, indent=2))

        # Then get detailed hotel info
        hotel_info = client.get_hotels(hotel_params)
        print("\nDetailed Hotel Info:")
       # print(json.dumps(hotel_info, indent=2))

        print(hotel_info)
    except Exception as e:
        print(f"Error: {str(e)}")
