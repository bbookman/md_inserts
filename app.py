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

    # --- Directory Handling ---
    # Instantiate File Handler - this also checks/creates the target directory
    file_handler = FILE_HANDLER()
    if not file_handler.target_dir:
        print("Exiting application because target directory is invalid or could not be created.")
        return

    target_dir = file_handler.target_dir # Use the validated directory path

    # --- API Key Check ---
    rapid_api_key = config.get("RAPID_API_KEY")
    if not rapid_api_key:
        print("WARNING: RAPID_API_KEY is not set. Skipping News, Weather, Movies, and Billboard API calls.")

    # --- Netflix Download ---
    netflix_password = getpass.getpass("Enter Netflix Password: ")
    if not netflix_password:
        print("Netflix password not provided. Skipping Netflix download and processing.")
        # Set password to None to indicate it wasn't provided for later checks
        netflix_password = None
    else:
        print("Downloading Netflix viewing history...")
        try:
            download_netflix_history(config, netflix_password)
            print("Netflix download function completed.")
        except Exception as e:
            print(f"ERROR downloading Netflix history: {e}")

    # --- REMOVED Redundant Yesterday File Processing Block ---
    # The logic to find and process only yesterday's file for API data has been removed.
    # The loop below handles all files.

    # --- Process Existing Files for API Data ---
    print(f"\n--- Processing API Data for files in {target_dir} ---")
    if not rapid_api_key:
        print("Skipping API data processing due to missing RAPID_API_KEY.")
    else:
        append_util = Append()
        processed_api_files = 0
        for file_name in os.listdir(target_dir):
            if file_name.endswith(".md"):
                file_path = os.path.join(target_dir, file_name)
                file_date_str = os.path.splitext(file_name)[0] # Expect YYYY-MM-DD

                print(f"\nChecking API data for: {file_name}")
                needs_update = False

                # Check and fetch News
                news_heading = "## News Headlines"
                if not file_handler.file_contains_section(file_path, news_heading):
                    print(f"  Fetching News data for {file_name}...")
                    news_markdown = fetch_and_process_api_data("NEWS", config)
                    if news_markdown:
                        append_util.append_to_file(file_path, news_markdown)
                        needs_update = True
                    else:
                         print(f"  No News data fetched.")
                else:
                    print(f"  News section already exists.")

                # Check and fetch Weather
                weather_heading = "## Weather"
                if not file_handler.file_contains_section(file_path, weather_heading):
                    print(f"  Fetching Weather data for {file_name}...")
                    weather_markdown = fetch_and_process_api_data("WEATHER", config)
                    if weather_markdown:
                        append_util.append_to_file(file_path, weather_markdown)
                        needs_update = True
                    else:
                        print(f"  No Weather data fetched.")
                else:
                    print(f"  Weather section already exists.")

                # Check and fetch Movies
                movies_heading = "## Top Box Office Movies"
                if not file_handler.file_contains_section(file_path, movies_heading):
                    print(f"  Fetching Movies data for {file_name}...")
                    movies_markdown = fetch_and_process_api_data("TOP_MOVIES", config)
                    if movies_markdown:
                        append_util.append_to_file(file_path, movies_markdown)
                        needs_update = True
                    else:
                        print(f"  No Movies data fetched.")
                else:
                    print(f"  Movies section already exists.")

                # Check and fetch Billboard
                billboard_heading = "## Billboard Hot 100"
                if not file_handler.file_contains_section(file_path, billboard_heading):
                    # Validate date format before making API call
                    try:
                        datetime.strptime(file_date_str, '%Y-%m-%d')
                        print(f"  Fetching Billboard data for date {file_date_str}...")
                        billboard_config = config.copy()
                        if 'BILLBOARD_PARAMS' not in billboard_config:
                            billboard_config['BILLBOARD_PARAMS'] = {}
                        billboard_config['BILLBOARD_PARAMS']['date'] = file_date_str
                        billboard_config['BILLBOARD_PARAMS']['range'] = '1-10'
                        billboard_markdown = fetch_and_process_api_data("BILLBOARD", billboard_config)
                        if billboard_markdown:
                            append_util.append_to_file(file_path, billboard_markdown)
                            needs_update = True
                        else:
                            print(f"  No Billboard data fetched for {file_date_str}.")
                    except ValueError:
                        print(f"  Skipping Billboard for {file_name}: Invalid date format '{file_date_str}'. Expected YYYY-MM-DD.")
                else:
                    print(f"  Billboard section already exists.")

                if needs_update:
                    processed_api_files += 1

        print(f"Finished processing API data. Updated {processed_api_files} file(s).")

    # --- Process Music History ---
    print(f"\n--- Processing Music History for files in {target_dir} ---")
    music_processor = MusicHistoryProcessor(config)
    music_processor.append_tracks_to_files()
    print("Music history processing complete.")

    # --- Process Netflix History ---
    print(f"\n--- Processing Netflix History (will create files if needed) ---")
    if netflix_password: # Only process if password was provided for download
        netflix_processor = NetflixHistoryProcessor(config)
        netflix_processor.append_shows_to_files()
        print("Netflix history processing complete.")
    else:
        print("Skipping Netflix history processing as password was not provided.")

    print("\nApplication finished.")

if __name__ == "__main__":
    main()