from datetime import datetime

import requests


def get_weather(city_name: str) -> dict:
    """
    Fetch current weather data from OpenWeatherMap API
    Returns formatted weather data as a dictionary
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": '615592c2ab513ecc73b86378e166ba3e',
        "units": "metric"  # Get temperatures in Celsius
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            return {"error": "No weather data available"}

        # Convert sunrise/sunset timestamps to readable format
        sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
        sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')

        return {
            "location": f"{data['name']}, {data['sys']['country']}",
            "coordinates": f"{data['coord']['lat']}°N, {data['coord']['lon']}°E",
            "temperature": f"{data['main']['temp']}°C",
            "feels_like": f"{data['main']['feels_like']}°C",
            "conditions": data['weather'][0]['description'].title(),
            "humidity": f"{data['main']['humidity']}%",
            "wind": f"{data['wind']['speed']} m/s at {data['wind']['deg']}°",
            "sunrise": sunrise,
            "sunset": sunset
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"API Error: {str(e)}"}
    except KeyError as e:
        return {"error": f"Data parsing error: Missing {str(e)} in response"}


if __name__ == "__main__":
    response = get_weather('Paris')
    print(response)
