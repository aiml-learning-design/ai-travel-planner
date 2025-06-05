import requests

def get_places(city_name: str, limit: int = 5):
    overpass_url = "https://overpass-api.de/api/interpreter"

    # Overpass QL with expanded filters for better tourist results
    query = f"""
    [out:json][timeout:25];
    area["name"="{city_name}"]->.searchArea;
    (
      node["tourism"~"attraction|museum|gallery|viewpoint"](area.searchArea);
      way["tourism"~"attraction|museum|gallery|viewpoint"](area.searchArea);
      relation["tourism"~"attraction|museum|gallery|viewpoint"](area.searchArea);

      node["historic"="monument"](area.searchArea);
      way["historic"="monument"](area.searchArea);
      relation["historic"="monument"](area.searchArea);

      node["amenity"="arts_centre"](area.searchArea);
    );
    out center {limit};
    """

    try:
        response = requests.post(overpass_url, data=query)
        data = response.json()

        if "elements" not in data or not data["elements"]:
            return {"error": "No attractions found."}

        results = []
        for el in data["elements"][:limit]:
            name = el.get("tags", {}).get("name")
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lon = el.get("lon") or el.get("center", {}).get("lon")
            if name and lat and lon:
                results.append({
                    "name": name,
                    "latitude": lat,
                    "longitude": lon
                })

        return {"results": results}

    except Exception as e:
        return {"error": str(e)}

# 🔍 Test the function
if __name__ == "__main__":
    places = get_places("Paris", limit=5)
    print(places)