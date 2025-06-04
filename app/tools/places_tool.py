# Fetch places to visit

import requests
from pathlib import Path
import sys
from requests.structures import CaseInsensitiveDict

from typing import List, Dict, Any
from app.core.configuration import GEOAPIFY_PLACES_API_KEY

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Constants
GEOCODING_URL = "https://api.geoapify.com/v1/geocode/autocomplete"
SEARCH_RADIUS = 5000  # meters around the location
MAX_RESULTS = 5


def get_places(location: str) -> str:
    params = {
        "text": location,
        "apiKey": GEOAPIFY_PLACES_API_KEY
    }

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    try:
        resp = requests.get(GEOCODING_URL, headers=headers, params=params, timeout=10)
        print(f"Response Status: {resp.status_code}")
        if resp.status_code != 200:
            return {"error": f"Received status code {resp.status_code}"}

        data = resp.json()
        features = data.get("features", [])[:2]  # Only first 2 places
        if not features:
            return {"error": "No locations found."}

        results = []
        for feature in features:
            props = feature.get("properties", {})
            place_info = {
                "formatted": props.get("formatted", "N/A"),
                "country": props.get("country", "N/A"),
                "state": props.get("state", "N/A"),
                "city": props.get("city", "N/A"),
                "latitude": props.get("lat", "N/A"),
                "longitude": props.get("lon", "N/A")
            }
            results.append(place_info)

        return {"results": results}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}


if __name__ == "__main__":
    # Test the function
    print(get_places("Paris"))
