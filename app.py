import json
import os
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
    
    # Download Netflix viewing history first
    print("Downloading Netflix viewing history...")
    download_netflix_history(config)
    
    # Get yesterday's file path first, so we can extract the date
    file_handler = FILE_HANDLER()
    yesterday_file = file_handler.get_yesturday_file()
    
    # Process API data only if yesterday's file exists
    if yesterday_file:
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
        print(f"Successfully appended API data to {yesterday_file}")
    else:
        print("Yesterday's file not found. Skipping API data processing.")
        # Optionally, uncomment these lines to create yesterday's file
        # target_dir = config.get('TARGET_DIR', '')
        # yesterday = datetime.now().strftime('%Y-%m-%d')
        # yesterday_file = os.path.join(target_dir, f"{yesterday}.md")
        # with open(yesterday_file, 'w', encoding='utf-8') as f:
        #     f.write(f"# Journal Entry {yesterday}\n\n")
        # print(f"Created new file: {yesterday_file}")

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