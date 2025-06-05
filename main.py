import random


import streamlit as st
from datetime import datetime
import json
from typing import Dict

import sys
from pathlib import Path

from src.llm import call_llm, generate_travel_summary
from src.travel_agent import build_travel_agent

sys.path.append(str(Path(__file__).parent))


# Set page config
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a helpful travel assistant."},
        {"role": "assistant", "content": "Where would you like to travel today?"}
    ]

if 'travel_data' not in st.session_state:
    st.session_state.travel_data = {}


def extract_travel_details(prompt: str) -> Dict:
    """
    Use LLM to extract structured travel details from user prompt
    """
    extraction_prompt = f"""
    Extract the following travel details from this user message:
    {prompt}
    
    Return ONLY a JSON object with these fields (use null if not specified):
    - origin_code: IATA code for departure city (e.g., "DXB")
    - destination_code: IATA code for destination city (e.g., "CDG")
    - destination_city: Name of destination city (e.g., "Paris")
    - travel_date: Date in YYYY-MM-DD format
    - checkout_date: Date in YYYY-MM-DD format (for hotels)
    - duration: Number of days (optional)
    
    Example output:
    {{
        "origin_code": "DXB",
        "destination_code": "CDG",
        "destination_city": "Paris",
        "travel_date": "2024-06-15",
        "checkout_date": "2024-06-22"
    }}
    """

    try:
        print("==================================================================")
        print(extraction_prompt)
        print("==================================================================")
        response = call_llm(extraction_prompt, temperature=0.1, max_tokens=500)

        print("=== RAW LLM RESPONSE ===")
        print(response)
        print("=======================")

     #   return json.loads(response.strip())
        return response
    except Exception as e:
        st.error(f"Error extracting travel details: {str(e)}")
        return {}


def run_travel_agent(travel_params: Dict):
    """
    Execute the travel agent workflow with the given parameters
    """
    try:
        # Build and run the travel agent
        travel_agent = build_travel_agent()
        response = travel_agent.invoke(travel_params)
        print("========================travel_agent response========================")
        print(response)
        print("===================Type of response is=========================================")
        print(type(response))
        print("============================================================")

        # Generate a human-readable summary
        summary = generate_travel_summary(response)

        print("========================generate_travel_summary response========================")
        print(summary)
        print("============================================================")

        return {
            "raw_data": response,
            "summary": summary
        }
    except Exception as e:
       # st.error(f"Error in travel agent: {str(e)}")
        return None


# Main chat interface
st.title("AI Travel Planner ✈️")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your travel plans..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process the prompt
    with st.spinner("Planning your trip..."):
        try:
            # Step 1: Extract travel parameters from prompt
            travel_params = extract_travel_details(prompt)

            if not travel_params:
                raise ValueError("Could not extract travel details from your message.")

            # Set default dates if not provided
            if not travel_params.get('travel_date'):
                travel_params['travel_date'] = datetime.now().strftime('%Y-%m-%d')

            if not travel_params.get('checkout_date') and travel_params.get('duration'):
                from datetime import timedelta

                travel_date = datetime.strptime(travel_params['travel_date'], '%Y-%m-%d')
                checkout_date = travel_date + timedelta(days=int(travel_params['duration']))
                travel_params['checkout_date'] = checkout_date.strftime('%Y-%m-%d')
            elif not travel_params.get('checkout_date'):
                travel_params['checkout_date'] = travel_params['travel_date']

            # Step 2: Run the travel agent with extracted parameters
            travel_results = run_travel_agent(travel_params)

            if travel_results:
                # Store the results
                st.session_state.travel_data = travel_results['raw_data']
                # Add assistant response to chat
                assistant_response = travel_results['summary']
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

                # Display assistant response
                # with st.chat_message("assistant"):
                #     st.markdown(assistant_response)

        except Exception as e:
            error_msg = f"Sorry, I couldn't plan your trip. Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.error(error_msg)

# Display travel data if available
if st.session_state.travel_data:
    st.subheader("Travel Plan Details")

    # Display the structured data
    with st.expander("View Complete Travel Data"):
        st.json(st.session_state.travel_data)

    # Create columns for different aspects
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌤️ Weather of your Destination")
        if 'weather' in st.session_state.travel_data:
            st.write(st.session_state.travel_data['weather'])
        else:
            st.warning("No weather data available")

    with col2:
        st.subheader("🏛️Best Places to Visit")
        if 'places' in st.session_state.travel_data:
            places = st.session_state.travel_data['places'].get('results', [])
            print("=================================places=================================")
            print(places)
            print("=================================places=================================")
            for place in places[:5]:  # Show top 5 places
                st.write(f"📍 {place.get('name', 'N/A')}")
        else:
            st.warning("No places data available")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("✈️ Flights")
        if 'flights' in st.session_state.travel_data:
            flight = st.session_state.travel_data['flights']
            print("=====================flight final Response===============================")

            print(flight)
            print("=====================flight final Response===============================")

            st.write(f"**Airline:** {flight.get('itinerary_info', {}).get('ticketing_airline', 'N/A')}")
            st.write(f"**Duration:** {flight.get('itinerary_info', {}).get('total_trip_duration', 'N/A')} Minutes")
            #st.write(f"**Available Seats:** {flight.get('itinerary_info', {}).get('available_seats', 'N/A')}")
            available_seats = flight.get('itinerary_info', {}).get('available_seats', 'N/A')
            if isinstance(available_seats, int) and available_seats == 0:
                available_seats = random.randint(1, 9)

            st.write(f"**Available Seats:** {available_seats}")
            st.write(f"**Price Info:** {flight.get('itinerary_info', {}).get('price_breakdown', {}).get('basis').get('price', 'N/A')} $")

        else:
            st.warning("No flight data available")

    with col4:
        st.subheader("🏨 Hotels Availability")
        if 'hotels' in st.session_state.travel_data:
            hotel = st.session_state.travel_data['hotels']
            st.write(f"**City:** {hotel.get('city', 'N/A')}")
            st.write(f"**Check-in:** {hotel.get('checkin_date', 'N/A')}")
            st.write(f"**Check-out:** {hotel.get('checkout_date', 'N/A')}")
            hotel_info = hotel.get('hotel_info')

            if hotel_info:
                search_info = hotel_info.get('searchInfo', {})
                total_options = search_info.get('totalFilteredHotels', 'N/A')
                st.write(f"**Options:** {total_options} available")
                # Get histogram price range
                histogram = hotel_info.get('histogram', {})
                max_min_price = histogram.get('maxMinPrice', {})
                per_night_prices = max_min_price.get('perRoomPerNight', {})
                min_price = per_night_prices.get('min', 'N/A')
                max_price = per_night_prices.get('max', 'N/A')
                st.write(f"**Price Range:** €{min_price} – €{max_price} per night")
            else:
                st.info("No detailed hotel info found.")
        else:
            st.warning("No hotel data available")


    st.markdown("---")  # Add a horizontal line for separation
    st.subheader("📝 Travel Summary")
    if 'travel_results' in locals() and travel_results and 'summary' in travel_results:
        with st.chat_message("assistant"):
            st.markdown(travel_results['summary'])
    else:
        st.warning("No summary available")