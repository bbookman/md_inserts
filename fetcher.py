from api_util import make_api_request
from utility_parser import UtilityParser
from markdown_generator import Markdown

def fetch_and_process_api_data(api_type, config):
    """
    Generic function to fetch and process data from any API.
    """
    # Get API endpoint and the single RapidAPI key
    endpoint = config.get(f'{api_type}_ENDPOINT')
    key = config.get("RAPID_API_KEY")
    params = config.get(f'{api_type}_PARAMS', {})
    
    # Check if endpoint is specified
    if not endpoint:
        print(f"WARNING: {api_type}_ENDPOINT is not set. Skipping {api_type} API data fetch.")
        return None
    
    # Special handling for WEATHER API: ensure latitude and longitude are included
    if api_type.upper() == "WEATHER":
        if "latitude" not in params:
            params["latitude"] = config.get("LATITUDE")
        if "longitude" not in params:
            params["longitude"] = config.get("LONGITUDE")
    
    print(f"Making {api_type} API request to: {endpoint}")
    print(f"With parameters: {params}")
    
    # Call the API
    data = make_api_request(key, endpoint, params)
    
    # Parse the response
    parser = UtilityParser()
    parse_method = getattr(parser, f'parse_{api_type.lower()}')
    parsed_data = parse_method(data)
    
    # Generate markdown
    markdown_generator = Markdown()
    generate_method = getattr(markdown_generator, f'generate_{api_type.lower()}_markdown')
    return generate_method(parsed_data)