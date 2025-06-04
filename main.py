import streamlit as st
from app.agents.travel_agent import build_travel_agent
from app.agents.llm import call_llm
import json

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

# Sidebar for travel parameters
with st.sidebar:
    st.title("Travel Parameters")
    origin = st.text_input("Departure City (IATA Code)", "DXB")
    destination = st.text_input("Destination City (IATA Code)", "CDG")
    destination_city = st.text_input("Destination City Name", "Paris")
    travel_date = st.date_input("Travel Date")
    checkout_date = st.date_input("Checkout Date")

    if st.button("Generate Travel Plan"):
        # Prepare travel state
        travel_state = {
            "origin_code": origin,
            "destination_code": destination,
            "destination_city": destination_city,
            "travel_date": str(travel_date),
            "checkout_date": str(checkout_date)
        }

        # Run the travel agent
        try:
            travel_agent = build_travel_agent()
            response = travel_agent.invoke(travel_state)
            st.session_state.travel_data = response
            st.success("Travel data fetched successfully!")
        except Exception as e:
            st.error(f"Error generating travel plan: {str(e)}")

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

    # Prepare context for LLM
    context = {
        "travel_data": st.session_state.travel_data,
        "chat_history": st.session_state.messages[:-1]  # Exclude current prompt
    }

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Combine prompt with context
                full_prompt = f"""
                Travel Context: {json.dumps(context['travel_data'], indent=2)}
                Chat History: {json.dumps(context['chat_history'], indent=2)}
                User Question: {prompt}
                
                Please provide a helpful response about the travel plans based on the above information.
                """

                response = call_llm(full_prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error generating response: {str(e)}")

# Display travel data if available
if st.session_state.travel_data:
    st.subheader("Travel Plan Details")
    with st.expander("View Complete Travel Data"):
        st.json(st.session_state.travel_data)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("🌤️ Weather")
        if 'weather' in st.session_state.travel_data:
            st.write(st.session_state.travel_data['weather'])

    with col2:
        st.subheader("🏨 Hotels")
        if 'hotels' in st.session_state.travel_data:
            hotel_info = st.session_state.travel_data['hotels']
            st.write(f"**City:** {hotel_info.get('city')}")
            st.write(f"**Check-in:** {hotel_info.get('checkin_date')}")
            st.write(f"**Check-out:** {hotel_info.get('checkout_date')}")

    with col3:
        st.subheader("✈️ Flights")
        if 'flights' in st.session_state.travel_data:
            flight_info = st.session_state.travel_data['flights']
            st.write(f"**Airline:** {flight_info['itinerary_info']['ticketing_airline']}")
            st.write(f"**Duration:** {flight_info['itinerary_info']['total_trip_duration']}")

    with col4:
        st.subheader("🏛️ Places to Visit")
        if 'places' in st.session_state.travel_data:
            places = st.session_state.travel_data['places']['results']
            for place in places[:3]:  # Show top 3 places
                st.write(f"📍 {place.get('formatted')}")