import json
import os
import getpass # Import getpass
from datetime import datetime
from file_handler import FILE_HANDLER
from file_append_util import Append
from fetcher import fetch_and_process_api_data
from music_history import MusicHistoryProcessor
from netflix_history import NetflixHistoryProcessor
from netflix_downloader import download_netflix_history

def load_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Load config
    config = load_config('config.json')
    
    # Check for RapidAPI Key before proceeding with API calls
    rapid_api_key = config.get("RAPID_API_KEY")
    if not rapid_api_key:
        print("WARNING: RAPID_API_KEY is not set in config.json. Skipping News, Weather, Movies, and Billboard API calls.")

    # Prompt for Netflix Password securely
    netflix_password = getpass.getpass("Enter Netflix Password: ")
    if not netflix_password:
        print("Netflix password not provided. Exiting.")
        return # Or handle as appropriate

    # Download Netflix viewing history first, passing the password
    print("Downloading Netflix viewing history...")
    try:
        download_netflix_history(config, netflix_password) # Pass password here
        print("Netflix download function completed.")
    except Exception as e:
        print(f"ERROR downloading Netflix history: {e}")
    
    # Get yesterday's file path first, so we can extract the date
    file_handler = FILE_HANDLER()
    yesterday_file = file_handler.get_yesturday_file()
    
    # Initialize markdown variables outside the conditional block
    news_markdown = ""
    weather_markdown = ""
    movies_markdown = ""
    billboard_markdown = ""
    file_date = None

    # Process API data only if yesterday's file exists AND RapidAPI key is present
    if yesterday_file and rapid_api_key:
        # Extract date from filename (assuming format like '2025-04-17.md')
        file_date = os.path.basename(yesterday_file).split('.')[0]  # Gets '2025-04-17'
        print(f"Extracted date from file: {file_date}")
        
        # Process news data
        print("Processing News data...")
        news_markdown = fetch_and_process_api_data("NEWS", config)
        
        # Process weather data
        print("Processing Weather data...")
        weather_markdown = fetch_and_process_api_data("WEATHER", config)
        
        # Process top movies data
        print("Processing Top Movies data...")
        movies_markdown = fetch_and_process_api_data("TOP_MOVIES", config)
        
        # Process Billboard data with date from filename
        print(f"Processing Billboard data for date: {file_date}")
        
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
        if news_markdown: append_util.append_to_file(yesterday_file, news_markdown)
        if weather_markdown: append_util.append_to_file(yesterday_file, weather_markdown)
        if movies_markdown: append_util.append_to_file(yesterday_file, movies_markdown)
        if billboard_markdown: append_util.append_to_file(yesterday_file, billboard_markdown)
        print(f"Successfully appended API data to {yesterday_file}")

    elif yesterday_file and not rapid_api_key:
        print("Skipping API data appending because RAPID_API_KEY is missing.")
    else:
        print("Yesterday's file not found. Skipping API data processing.")

    # Process music history regardless of yesterday's file existence
    print("Processing music history for all markdown files...")
    music_processor = MusicHistoryProcessor(config)
    music_processor.append_tracks_to_files()
    print("Music history processing complete.")
    
    # After music history processing
    print("Processing Netflix history for all markdown files...")
    netflix_processor = NetflixHistoryProcessor(config)
    netflix_processor.append_shows_to_files()
    print("Netflix history processing complete.")

if __name__ == "__main__":
    main()