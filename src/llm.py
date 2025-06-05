import os

import pandas as pd
import requests
from typing import List, Dict, Optional

import json

from src.configuration import GROQ_API_KEY, GROQ_ENDPOINT

MODEL = "llama3-70b-8192"

# System prompt for travel assistant
TRAVEL_SYSTEM_PROMPT = """
You are an expert AI travel assistant specialized in creating comprehensive travel plans. 
Your responses should be:
1. Informative and detailed
2. Well-structured with clear sections
3. Include relevant information from the provided travel data
4. Friendly and helpful in tone

When discussing travel plans, always consider:
- Weather conditions at the destination
- Available flights and their details
- Hotel options and amenities
- Points of interest and attractions
- Practical travel advice

Format your responses with Markdown for better readability.
"""


def call_llm(
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
) -> dict:
    """
    Call the LLM with a single prompt.

    Args:
        prompt: Us  er's input prompt
        temperature: Creativity parameter (0-1)
        max_tokens: Maximum length of response
        model: Override default model
        system_prompt: Override default system prompt

    Returns:
        Generated response from LLM
    """
    #
    global content
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            #   {"role": "system", "content": system_prompt or TRAVEL_SYSTEM_PROMPT},
            {"role": "system", "content": "You are a helpful travel assistant that ONLY responds with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(GROQ_ENDPOINT, headers=headers, json=data, timeout=100)

        # Add debug logging
        # print(f"Request payload: {json.dumps(data, indent=2)}")
        # print(f"Status code: {response.status_code}")
        # print(f"Response: {response.text}")

        response.raise_for_status()
        completion = response.json()
        print("=== completion RESPONSE ===")
        #  print(completion)
        print("=======================")
        content = completion["choices"][0]["message"]["content"]
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {str(e)}\nResponse was: {content}")


# def chat_with_llm(
#         messages: List[Dict[str, str]],
#         temperature: float = 0.7,
#         max_tokens: int = 1024,
#         model: Optional[str] = None,
#         system_prompt: Optional[str] = None
# ) -> str:
#     """
#     Chat interface with message history.
#
#     Args:
#         messages: List of message dicts with role/content
#         temperature: Creativity parameter (0-1)
#         max_tokens: Maximum length of response
#         model: Override default model
#         system_prompt: Override default system prompt
#
#     Returns:
#         Generated response from LLM
#     """
#     headers = {
#         "Authorization": f"Bearer {GROQ_API_KEY}",
#         "Content-Type": "application/json"
#     }
#
#     # Prepend system prompt if provided
#     if system_prompt:
#         messages = [{"role": "system", "content": system_prompt}] + messages
#
#     data = {
#         "model": model or MODEL,
#         "messages": messages,
#         "temperature": temperature,
#         "max_tokens": max_tokens
#     }
#
#     try:
#         response = requests.post(GROQ_ENDPOINT, headers=headers, json=data)
#         response.raise_for_status()
#         completion = response.json()
#         return completion["choices"][0]["message"]["content"]
#     except Exception as e:
#         raise Exception(f"LLM API error: {str(e)}")


def generate_travel_summary(travel_data: Dict) -> dict:
    """
    Generate a comprehensive travel summary from the collected data.
    Enhanced to better utilize all available data points.
    """
    print(f"Input is =============================== {Dict}")

    # Extract and structure the data
    structured_data = {
        "trip": {
            "origin": f"{travel_data.get('origin_code')} (Dubai)",
            "destination": f"{travel_data.get('destination_city')} ({travel_data.get('destination_code')})",
            "dates": f"{travel_data.get('travel_date')} to {travel_data.get('checkout_date')}",
            "duration": f"{(pd.to_datetime(travel_data['checkout_date']) - pd.to_datetime(travel_data['travel_date'])).days} days"
        },
        "weather": {
            "conditions": travel_data.get('weather', {}).get('conditions'),
            "temperature": travel_data.get('weather', {}).get('temperature'),
            "recommendation": "Bring an umbrella" if "rain" in travel_data.get('weather', {}).get('conditions',
                                                                                                  '').lower() else "Pleasant weather expected"
        },
        "flight": {
            "airline": travel_data.get('flights', {}).get('itinerary_info', {}).get('ticketing_airline'),
            "duration": f"{travel_data.get('flights', {}).get('itinerary_info', {}).get('total_trip_duration', 0) // 60}h {travel_data.get('flights', {}).get('itinerary_info', {}).get('total_trip_duration', 0) % 60}m",
            "price": f"€{travel_data.get('flights', {}).get('itinerary_info', {}).get('price_breakdown', {}).get('basis', {}).get('total', {}).get('inc', 'N/A')}",
            "seats": travel_data.get('flights', {}).get('itinerary_info', {}).get('available_seats')
        },
        "accommodation": {
            "options": travel_data.get('hotels', {}).get('hotel_info', {}).get('searchInfo', {}).get(
                'totalFilteredHotels'),
            "price_range": get_price_range(travel_data.get('hotels', {}).get('hotel_info', {}).get('histogram')),
            "urgency": travel_data.get('hotels', {}).get('hotel_info', {}).get('urgencyDetail', {}).get('urgencyScore')
        },
        "places": {
            "main": travel_data.get('destination_city'),
            "districts": [
                p.get('formatted', p.get('name', 'Unknown location'))
                for p in travel_data.get('places', {}).get('results', [])
                if isinstance(p, dict)
            ],
            "recommendations": [
                "Eiffel Tower (7th arrondissement)",
                "Louvre Museum (1st arrondissement)",
                "Notre-Dame Cathedral (4th arrondissement)",
                "Montmartre (18th arrondissement)",
                "Champs-Élysées (8th arrondissement)"
            ]
        }
    }

    prompt = f"""
    Create a detailed travel summary using the following structured data:
    {json.dumps(structured_data, indent=2)}

    Format your response with these sections:
    
    ## Trip Overview
    - ✈️ {structured_data['trip']['origin']} → {structured_data['trip']['destination']}
    - 📅 {structured_data['trip']['dates']} ({structured_data['trip']['duration']} stay)
    
    ## Weather Forecast
    - ⛅ Conditions: {structured_data['weather']['conditions']}
    - 🌡️ Temperature: {structured_data['weather']['temperature']}
    - 🧳 Recommendation: {structured_data['weather']['recommendation']}
    
    ## Flight Details
    - 🛫 Airline: {structured_data['flight']['airline']}
    - ⏱️ Duration: {structured_data['flight']['duration']}
    - 💰 Price: {structured_data['flight']['price']}
    - 🪑 Seats Available: {structured_data['flight']['seats']}
    
    ## Accommodation
    - 🏨 Options Available: {structured_data['accommodation']['options']}
    - 💲 Price Range: {structured_data['accommodation']['price_range']}
    - ⚠️ Booking Urgency: {'High' if structured_data['accommodation'].get('urgency', 0) > 70 else 'Moderate'}
    
    ## Recommended Places
    - Must-see attractions in {structured_data['places']['main']}:
      {chr(10).join('      • ' + place for place in structured_data['places']['recommendations'])}
    - Popular districts: {', '.join(structured_data['places']['districts'][:3])}
    
    ## Travel Tips
    - Best times to visit popular sites
    - Local transportation advice
    - Cultural notes
    
    Use Markdown formatting with emojis for better readability.
    Include only information derived from the provided data.
    """

    try:
        response = call_llm(
            prompt,
            temperature=0.3,
            max_tokens=1200
        )
        return response
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def get_price_range(histogram):
    if not histogram or not histogram.get('bins'):
        return "Not available"
    bins = histogram['bins']
    min_price = bins[0].get('upperBound')['perNightPerRoom']
    max_price = bins[-1].get('upperBound')['perNightPerRoom']
    return f"€{min_price}-€{max_price} per night"


if __name__ == "__main__":
    # Test the LLM with a travel-related query
    test_prompt = """Extract the following travel details from this user message:
    Please plan my travel from Dubai to Paris on 15 June 2025 to 20 June 2025
    
    Return ONLY a JSON object with these fields (use null if not specified):
        - origin_code: IATA code for departure city (e.g., "DXB")
        - destination_code: IATA code for destination city (e.g., "CDG")
        - destination_city: Name of destination city (e.g., "Paris")
        - travel_date: Date in YYYY-MM-DD format
        - checkout_date: Date in YYYY-MM-DD format (for hotels)
        - duration: Number of days (optional)
    
    Example output:
    {
        "origin_code": "DXB",
        "destination_code": "CDG",
        "destination_city": "Paris",
        "travel_date": "2024-06-15",
        "checkout_date": "2024-06-22"
    }
    """
   # response = call_llm(test_prompt)
  #  print(json.dumps(response, indent=2))

    test_response = """
            {
          "origin_code": "DXB",
          "destination_code": "CDG",
          "destination_city": "Paris",
          "travel_date": "2025-06-15",
          "checkout_date": "2025-06-20",
          "weather": {
            "location": "Paris, FR",
            "coordinates": "48.8534°N, 2.3488°E",
            "temperature": "15.16°C",
            "feels_like": "14.9°C",
            "conditions": "Light Rain",
            "humidity": "83%",
            "wind": "4.9 m/s at 209°",
            "sunrise": "07:49",
            "sunset": "23:49"
          },
          "places": {
            "results": [
              {
                "formatted": "Paris, IDF, France",
                "country": "France",
                "state": "Ile-de-France",
                "city": "Paris",
                "latitude": 48.8588897,
                "longitude": 2.3200410217200766
              },
              {
                "formatted": "16th Arrondissement, Paris, IDF, France",
                "country": "France",
                "state": "Ile-de-France",
                "city": "Paris",
                "latitude": 48.8631709,
                "longitude": 2.2757648
              }
            ]
          },
          "flights": {
            "itinerary_info": {
              "available_seats": 9,
              "ticketing_airline": "PC",
              "total_trip_duration": 650,
              "price_breakdown": {
                "basis": {
                  "basis": "PAPB",
                  "option": "Mandatory",
                  "price": {
                    "exc": 127.42,
                    "inc": 213.83
                  },
                  "quantity": 1,
                  "total": {
                    "exc": 127.42,
                    "inc": 213.83
                  }
                }
              }
            }
          },
          "hotels": {
            "city": "Paris",
            "checkin_date": "2025-06-15",
            "checkout_date": "2025-06-20",
            "hotel_info": {
              "searchInfo": {
                "totalActiveHotels": 24923,
                "totalFilteredHotels": 2989,
                "totalAvailableHotelsWithoutFilter": 2991,
                "searchStatus": {
                  "searchStatus": "Normal",
                  "searchCriteria": {
                    "checkIn": "2025-06-15T00:00:00.000+07:00"
                  }
                },
                "objectInfo": {
                  "cityId": 15470,
                  "cityName": "Paris",
                  "cityEnglishName": "Paris",
                  "countryId": 153,
                  "countryName": "France",
                  "countryEnglishName": "France",
                  "centerLatitude": 48.856667,
                  "centerLongitude": 2.350987,
                  "objectName": "Paris"
                },
                "isComplete": true,
                "hasSecretDeal": true,
                "hasInsiderDeal": false,
                "pollingInfoResponse": null,
                "hasEscapesPackage": true
              },
              "urgencyDetail": {
                "urgencyScore": 87
              },
              "histogram": {
                "bins": [
                  {
                    "numOfElements": 1,
                    "upperBound": {
                      "perNightPerRoom": 20,
                      "perBooking": 30
                    }
                  },
                  {
                    "numOfElements": 3,
                    "upperBound": {
                      "perNightPerRoom": 30,
                      "perBooking": 50
                    }
                  },
                  {
                    "numOfElements": 6,
                    "upperBound": {
                      "perNightPerRoom": 40,
                      "perBooking": 70
                    }
                  },
                  {
                    "numOfElements": 10,
                    "upperBound": {
                      "perNightPerRoom": 50,
                      "perBooking": 100
                    }
                  },
                  {
                    "numOfElements": 29,
                    "upperBound": {
                      "perNightPerRoom": 70,
                      "perBooking": 150
                    }
                  },
                  {
                    "numOfElements": 90,
                    "upperBound": {
                      "perNightPerRoom": 100,
                      "perBooking": 220
                    }
                  },
                  {
                    "numOfElements": 142,
                    "upperBound": {
                      "perNightPerRoom": 150,
                      "perBooking": 320
                    }
                  },
                  {
                    "numOfElements": 166,
                    "upperBound": {
                      "perNightPerRoom": 200,
                      "perBooking": 480
                    }
                  },
                  {
                    "numOfElements": 348,
                    "upperBound": {
                      "perNightPerRoom": 290,
                      "perBooking": 710
                    }
                  },
                  {
                    "numOfElements": 514,
                    "upperBound": {
                      "perNightPerRoom": 400,
                      "perBooking": 1060
                    }
                  },
                  {
                    "numOfElements": 334,
                    "upperBound": {
                      "perNightPerRoom": 570,
                      "perBooking": 1570
                    }
                  },
                  {
                    "numOfElements": 163,
                    "upperBound": {
                      "perNightPerRoom": 800,
                      "perBooking": 2320
                    }
                  },
                  {
                    "numOfElements": 109,
                    "upperBound": {
                      "perNightPerRoom": 1120,
                      "perBooking": 3450
                    }
                  },
                  {
                    "numOfElements": 48,
                    "upperBound": {
                      "perNightPerRoom": 1570,
                      "perBooking": 5110
                    }
                  },
                  {
                    "numOfElements": 112,
                    "upperBound": {
                      "perNightPerRoom": 2210,
                      "perBooking": 7580
                    }
                  },
                  {
                    "numOfElements": 34,
                    "upperBound": {
                      "perNightPerRoom": 3100,
                      "perBooking": 11250
                    }
                  },
                  {
                    "numOfElements": 10,
                    "upperBound": {
                      "perNightPerRoom": 4360,
                      "perBooking": 16680
                    }
                  },
                  {
                    "numOfElements": 3,
                    "upperBound": {
                      "perNightPerRoom": 6130,
                      "perBooking": 24750
                    }
                  },
                  {
                    "numOfElements": 6,
                    "upperBound": {
                      "perNightPerRoom": 8620,
                      "perBooking": 36700
                    }
                  },
                  {
                    "numOfElements": 41,
                    "upperBound": {
                      "perNightPerRoom": 12120,
                      "perBooking": 54440
                    }
                  },
                  {
                    "numOfElements": 5,
                    "upperBound": {
                      "perNightPerRoom": 17040,
                      "perBooking": 80750
                    }
                  },
                  {
                    "numOfElements": 12,
                    "upperBound": {
                      "perNightPerRoom": 23950,
                      "perBooking": 119770
                    }
                  }
                ],
                "maxMinPrice": {
                  "perRoomPerNight": {
                    "max": 23954,
                    "median": null,
                    "min": 0
                  },
                  "perBook": {
                    "max": 119768,
                    "median": null,
                    "min": 0
                  }
                }
              },
              "isFreeTextSortMatch": null,
              "nhaProbability": "Low",
              "cid": 1605717
            }
          }
        }
    """

    test_response = json.loads(test_response)
    summary = generate_travel_summary(test_response)
    print("=====================FINAL Response===============================")
    print(json.dumps(summary, indent=2))
    print("=====================FINAL Response===============================")
