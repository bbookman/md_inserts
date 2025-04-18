import requests
from typing import Dict, Any, Optional
import json
from urllib.parse import urlencode

def make_api_request(api_key: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[Any, Any]:
    """
    Makes an API request with the given credentials and parameters.
    
    Args:
        api_key (str): The API key for authentication.
        endpoint (str): The API endpoint URL.
        params (dict, optional): Query parameters for the request.
        
    Returns:
        dict: The JSON response from the API.
    """
    headers = {
        'x-rapidapi-host': endpoint.split('/')[2],
        'x-rapidapi-key': api_key
    }
    
    # Debug info
    print(f"\nMaking request to: {endpoint}")
    print(f"With parameters: {params}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        
        # Print the actual URL that was requested
        print(f"Actual request URL: {response.url}")
        
        # Print response status
        print(f"Response status: {response.status_code}")
        
        # Try to print some of the response text
        print(f"Response preview: {response.text[:100]}...")
        
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return {"ERROR": str(e)}

