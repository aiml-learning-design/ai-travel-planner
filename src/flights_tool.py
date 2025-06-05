import http.client
import os
import json
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from src.configuration import FLIGHT_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FlightSearchParams:
    origin: str
    destination: str
    departure_date: str  # Format: "YYYY-MM-DD"
    adults: int = 1
    currency: str = "USD"  # Default currency


class FlightAPIClient:
    def __init__(
            self,
            api_key: Optional[str] = None,
            api_host: str = "agoda-com.p.rapidapi.com",
            base_endpoint: str = "/flights",
    ):
        """
        Initialize the Flight API client.

        Args:
            api_key: If not provided, tries to load from `FLIGHT_API_KEY` env var.
            api_host: API host (default: Agoda's RapidAPI host).
            base_endpoint: Base path for flight endpoints.
        """
        self.api_key = FLIGHT_API_KEY
        if not self.api_key:
            raise ValueError("Flight API key not provided and FLIGHT_API_KEY env var not set")

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
    def get_flights(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Generic method to make HTTP requests to the Flight API.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint (e.g., "/search-one-way").
            params: Query parameters.

        Returns:
            Parsed JSON response.

        Raises:
            ValueError: If the API returns an error.
        """
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

    def search_one_way(self, params: FlightSearchParams) -> Dict:
        """
        Search for one-way flights.

        Args:
            params: FlightSearchParams object with search criteria.

        Returns:
            Flight search results (parsed JSON).
        """
        endpoint = "/search-one-way"
        api_params = {
            "origin": params.origin,
            "destination": params.destination,
            "departureDate": params.departure_date,
            "adults": params.adults,
            "currency": params.currency,
        }
        results = self.get_flights("GET", endpoint, api_params)
        itineraries = results['data']['bundles'][0]['itineraries']
        first_itinerary = itineraries[0]  # or result['data']['bundles'][0]['itineraries'][0]
        itinerary_info = first_itinerary['itineraryInfo']

        itinerary_dict = {
            "itinerary_info": {
                "available_seats": itinerary_info["availableSeats"],
                "ticketing_airline": itinerary_info["ticketingAirline"],
                "total_trip_duration": itinerary_info["totalTripDuration"],
                "price_breakdown": {
                    "basis": itinerary_info["price"]["usd"]["charges"][0]["breakDown"][0]
                }
            }
        }
        return itinerary_dict

    def search_round_trip(
            self,
            params: FlightSearchParams,
            return_date: str,
    ) -> Dict:
        """
        Search for round-trip flights.

        Args:
            params: FlightSearchParams for the outbound flight.
            return_date: Date for the return flight (format: "YYYY-MM-DD").

        Returns:
            Flight search results (parsed JSON).
        """
        endpoint = "/search-round-trip"
        api_params = {
            "origin": params.origin,
            "destination": params.destination,
            "departureDate": params.departure_date,
            "returnDate": return_date,
            "adults": params.adults,
            "currency": params.currency,
        }
        return self.get_flights("GET", endpoint, api_params)


if __name__ == "__main__":
    client = FlightAPIClient()  # Auto-loads API key from env

    # One-way search
    one_way_params = FlightSearchParams(
        origin="DXB",
        destination="CDG",
        departure_date="2025-06-26",
    )
    results = client.search_one_way(one_way_params)

    print(results)

