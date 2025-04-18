import json
import os
from file_handler import FILE_HANDLER
from file_append_util import Append
from fetcher import fetch_and_process_api_data

def load_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Load config
    config = load_config('config.json')
    
    # Get yesterday's file path first, so we can extract the date
    file_handler = FILE_HANDLER()
    yesterday_file = file_handler.get_yesturday_file()
    
    if not yesterday_file:
        print("Yesterday's file not found")
        return
    
    # Extract date from filename (assuming format like '2025-04-17.md')
    file_date = os.path.basename(yesterday_file).split('.')[0]  # Gets '2025-04-17'
    print(f"Extracted date from file: {file_date}")
    
    # Process news data
    news_markdown = fetch_and_process_api_data("NEWS", config)
    
    # Process weather data
    weather_markdown = fetch_and_process_api_data("WEATHER", config)
    
    # Process top movies data
    print(f"Making TOP_MOVIES API request to: {config['TOP_MOVIES_ENDPOINT']}")
    movies_markdown = fetch_and_process_api_data("TOP_MOVIES", config)
    
    # Process Billboard data with date from filename
    print(f"Making BILLBOARD API request for date: {file_date}")
    
    # Create a copy of config to modify for this specific call
    billboard_config = config.copy()
    
    # Add both required parameters
    if 'BILLBOARD_PARAMS' not in billboard_config:
        billboard_config['BILLBOARD_PARAMS'] = {}

    billboard_config['BILLBOARD_PARAMS']['date'] = file_date  # Use the file date
    billboard_config['BILLBOARD_PARAMS']['range'] = '1-10'    # Add the range parameter which is required

    billboard_markdown = fetch_and_process_api_data("BILLBOARD", billboard_config)
    
    # Append the markdown to the file
    append_util = Append()
    append_util.append_to_file(yesterday_file, news_markdown)
    append_util.append_to_file(yesterday_file, weather_markdown)
    append_util.append_to_file(yesterday_file, movies_markdown)
    append_util.append_to_file(yesterday_file, billboard_markdown)
    print(f"Successfully appended data to {yesterday_file}")

if __name__ == "__main__":
    main()