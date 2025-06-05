from app.agents.travel_agent import build_travel_agent

# Step 1: Build the travel agent graph
travel_agent = build_travel_agent()

# Step 2: Define the initial state (input)
initial_state = {
    "origin_code": "DXB",  # Dubai
    "destination_code": "CDG",  # Paris
    "destination_city": "Paris",
    "travel_date": "2025-06-15",
    "checkout_date": "2025-06-20",
    "weather": None,
    "places": None,
    "flights": None,
    "hotels": None
}

# Step 3: Run the graph with initial input
final_state = travel_agent.invoke(initial_state)

# Step 4: Print the final output state
print("Real-time travel plan response:")
print("Weather:", final_state.get("weather"))
print("Places:", final_state.get("places"))
print("Flights:", final_state.get("flights"))
print("Hotels:", final_state.get("hotels"))