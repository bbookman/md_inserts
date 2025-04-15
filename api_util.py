import requests
from typing import Dict, Any, Optional
import json
from urllib.parse import urlencode

def make_api_request(api_key: str, end_point: str, params: Optional[Dict[str, Any]] = None) -> Dict[Any, Any]:
    """
    Makes an API request using RapidAPI-style headers with optional query parameters
    
    Args:
        api_key (str): The API key for authentication
        end_point (str): The API endpoint URL
        params (Optional[Dict[str, Any]]): Optional query parameters to append to the URL
        
    Returns:
        Dict[Any, Any]: The JSON response from the API
    """
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': end_point.split('//')[1].split('/')[0]
    }
    
    # Append query parameters to the URL if provided
    if params:
        url = f"{end_point}?{urlencode(params)}"
    else:
        url = end_point
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return {}

# Example usage:
if __name__ == "__main__":
    with open('config.json') as f:
        config = json.load(f)
    
    # Example with query parameters
    params = {
        "limit": 10,
        "offset": 0,
        "category": "technology"
    }
    
    result = make_api_request(
        api_key=config['NEWS_KEY'],
        end_point=config['NEWS_ENDPOINT'],
        params=params
    )
    print(result)