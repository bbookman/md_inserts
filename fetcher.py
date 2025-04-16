from api_util import make_api_request
from utility_parser import UtilityParser
from markdown_generator import Markdown

def fetch_and_process_api_data(api_type, config):
    """
    Generic function to fetch and process data from any API
    
    Args:
        api_type: String identifier for the API (e.g., "NEWS", "WEATHER")
        config: Configuration dictionary
        
    Returns:
        Markdown content ready for insertion
    """
    # Get API credentials and parameters
    endpoint = config.get(f'{api_type}_ENDPOINT')
    key = config.get(f'{api_type}_KEY')
    params = config.get(f'{api_type}_PARAMS', {})
    
    # For weather, add latitude/longitude if available
    if api_type == "WEATHER" and "latitude" not in params and "longitude" not in params:
        params['latitude'] = config.get('LATITUDE')
        params['longitude'] = config.get('LONGITUDE')
    
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