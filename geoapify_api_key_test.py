import requests
from requests.structures import CaseInsensitiveDict
import requests


def test_geoapify_api():
    url = "https://api.geoapify.com/v1/geocode/autocomplete?text=Mosco&apiKey=5c79dbab75b646db982c9dcb81652e60"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    resp = requests.get(url, headers=headers, timeout=10)
    print(resp.content)
    print(resp.status_code)


def test_groq_api():
    # API configuration
    url = "https://api.groq.com/openai/v1/chat/completions"
    api_key = "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"  # Replace with your actual key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [{
            "role": "user",
            "content": "Explain the importance of fast language models"
        }]
    }

    try:
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Process the response
        result = response.json()
        print("API Response:")
        print(f"Model: {result['model']}")
        print(f"Completion: {result['choices'][0]['message']['content']}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None


if __name__ == "__main__":
    print("------------------------------test_groq_api------------------------------")
   # test_groq_api()
    print("------------------------------test_geoapify_api------------------------------")
    test_geoapify_api()
