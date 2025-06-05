# app/agent/travel_agent.py

from langgraph.graph import StateGraph
from typing import TypedDict, Optional, List

from app.agents.flights_tool import FlightAPIClient, FlightSearchParams
from app.agents.hotels_tool import HotelAPIClient, HotelSearchParams
from app.agents.places_tool import get_places
from app.agents.weather_tool import get_weather


# from app.tools.weather_tool import get_weather
# from app.tools.places_tool import get_places
# from app.tools.flights_tool import FlightAPIClient, FlightSearchParams
# from app.tools.hotels_tool import HotelAPIClient, HotelSearchParams


# 1. Define the shared TravelState
class TravelState(TypedDict):
    origin_code: Optional[str] # Example : DXB For Dubai
    destination_code: Optional[str] # Example : CDG for Paris
    destination_city: Optional[str]
    travel_date: Optional[str]
    checkout_date: Optional[str]
    weather: Optional[str]
    places: Optional[List[str]]
    flights: Optional[List[str]]
    hotels: Optional[List[str]]


# 2. Define all the node functions

def fetch_weather(state: TravelState) -> TravelState:
    if "destination_city" not in state:
        raise ValueError("Missing 'destination_city' in TravelState")
    weather = get_weather(state["destination_city"])
    return {**state, "weather": weather}


def fetch_places(state: TravelState) -> TravelState:
    if "destination_city" not in state:
        raise ValueError("Missing 'destination_city' in TravelState")
    places = get_places(state["destination_city"])
    print("Places fetched")
    return {**state, "places": places}


def fetch_flights(state: TravelState) -> TravelState:
    if "origin_code" not in state:
        raise ValueError("Missing 'origin' of Travel")
    if "destination_code" not in state:
        raise ValueError("Missing 'destination' of Travel")
    if "travel_date" not in state:
        raise ValueError("Missing 'travel_date' of Travel")

    client = FlightAPIClient()

    one_way_params = FlightSearchParams(
        origin=state["origin_code"],
        destination=state["destination_code"],
        departure_date=state["travel_date"]
    )

    flights = client.search_one_way(one_way_params)
    print("Flights fetched")
    return {**state, "flights": flights}


def fetch_hotels(state: TravelState) -> TravelState:
    if "destination_city" not in state:
        raise ValueError("Missing 'destination_city' of Travel")
    if "travel_date" not in state:
        raise ValueError("Missing 'Date' of Travel")
    if "checkout_date" not in state:
        raise ValueError("Missing 'travel_date' of Travel")

    client = HotelAPIClient()
    # city_name = places_data["results"][0]["city"]
    hotel_params = HotelSearchParams(
        city=state["destination_city"],
        checkin_date=state["travel_date"],
        checkout_date=state["checkout_date"],
        adults=2,
        currency="EUR"
    )
    hotels = client.get_hotels(hotel_params)
    print("Hotels fetched")
    return {**state, "hotels": hotels}


# 3. Build LangGraph Travel Agent
def build_travel_agent():
    graph = StateGraph(TravelState)

    graph.add_node("get_weather", fetch_weather)
    graph.add_node("get_places", fetch_places)
    graph.add_node("get_flights", fetch_flights)
    graph.add_node("get_hotels", fetch_hotels)

    graph.set_entry_point("get_weather")
    graph.add_edge("get_weather", "get_places")
    graph.add_edge("get_places", "get_flights")
    graph.add_edge("get_flights", "get_hotels")

    graph.set_finish_point("get_hotels")

    return graph.compile()
