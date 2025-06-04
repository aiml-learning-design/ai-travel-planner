import os
import requests
from typing import List, Dict, Optional

from streamlit import json

from app.core.configuration import GROQ_API_KEY, GROQ_ENDPOINT

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
) -> str:
    """
    Call the LLM with a single prompt.
    
    Args:
        prompt: User's input prompt
        temperature: Creativity parameter (0-1)
        max_tokens: Maximum length of response
        model: Override default model
        system_prompt: Override default system prompt
    
    Returns:
        Generated response from LLM
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model or MODEL,
        "messages": [
            {"role": "system", "content": system_prompt or TRAVEL_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(GROQ_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        completion = response.json()
        return completion["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"LLM API error: {str(e)}")


def chat_with_llm(
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
) -> str:
    """
    Chat interface with message history.
    
    Args:
        messages: List of message dicts with role/content
        temperature: Creativity parameter (0-1)
        max_tokens: Maximum length of response
        model: Override default model
        system_prompt: Override default system prompt
    
    Returns:
        Generated response from LLM
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Prepend system prompt if provided
    if system_prompt:
        messages = [{"role": "system", "content": system_prompt}] + messages

    data = {
        "model": model or MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(GROQ_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        completion = response.json()
        return completion["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"LLM API error: {str(e)}")


def generate_travel_summary(travel_data: Dict) -> str:
    """
    Generate a comprehensive travel summary from the collected data.
    
    Args:
        travel_data: Dictionary containing all travel information
        
    Returns:
        Formatted travel summary
    """
    prompt = f"""
    Please create a detailed travel summary based on the following data:
    {json.dumps(travel_data, indent=2)}
    
    The summary should include:
    1. An overview of the trip
    2. Weather conditions
    3. Flight options
    4. Hotel recommendations
    5. Points of interest
    6. Any practical travel tips
    
    Use Markdown formatting with appropriate headings and bullet points.
    """

    return call_llm(prompt, temperature=0.5, max_tokens=1500)


if __name__ == "__main__":
    # Test the LLM with a travel-related query
    test_prompt = "I'm planning a trip to Paris in June. What should I pack?"
    print(call_llm(test_prompt))
