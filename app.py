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
from fandango_downloader import download_fandango_history  # Import the new Fandango downloader
from fandango_history import FandangoHistoryProcessor  # Import the new Fandango history processor
from yelp_parser import YelpReviewProcessor  # Import the new YelpReviewProcessor class
from ticketmaster_parser import TicketmasterProcessor  # Import the new TicketmasterProcessor class

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
        
    # --- Netflix Configuration Check ---
    netflix_file_location = config.get("NETFLIX_FILE_LOCATION")
    netflix_history_url = config.get("NETFLIX_HISTORY_URL")
    netflix_email_address = config.get("NETFLIX_EMAIL_ADDRESS")
    
    # Skip Netflix processing if any required Netflix config is missing
    if not netflix_file_location or not netflix_history_url or not netflix_email_address:
        if not netflix_file_location:
            print("WARNING: NETFLIX_FILE_LOCATION is not set. Skipping Netflix download and processing.")
        if not netflix_history_url:
            print("WARNING: NETFLIX_HISTORY_URL is not set. Skipping Netflix download and processing.")
        if not netflix_email_address:
            print("WARNING: NETFLIX_EMAIL_ADDRESS is not set. Skipping Netflix download and processing.")
        netflix_password = None  # Skip Netflix processing
        download_succeeded = False
    else:
        # --- Netflix Download ---
        netflix_password = getpass.getpass("Enter Netflix Password: ")
        download_succeeded = False # Initialize flag
        if not netflix_password:
            print("Netflix password not provided. Skipping Netflix download and processing.")
            # Set password to None to indicate it wasn't provided for later checks
            netflix_password = None
        else:
            print("Downloading Netflix viewing history...")
            try:
                # Capture the return value
                download_succeeded = download_netflix_history(config, netflix_password)
                if download_succeeded:
                    print("Netflix download function completed successfully.")
                else:
                    print("Netflix download function completed but reported failure.")
            except Exception as e:
                print(f"ERROR during Netflix download call: {e}")
                download_succeeded = False # Ensure flag is false on exception

    # --- REMOVED Redundant Yesterday File Processing Block ---
    # The logic to find and process only yesterday's file for API data has been removed.
    # The loop below handles all files.

    # --- Process Existing Files for API Data ---
    print(f"\n--- Processing API Data for files in {target_dir} and subdirectories ---")
    if not rapid_api_key:
        print("Skipping API data processing due to missing RAPID_API_KEY.")
    else:
        append_util = Append()
        processed_api_files = 0
        # Use os.walk for recursive search
        for root, dirs, files in os.walk(target_dir):
            for file_name in files:
                if file_name.endswith(".md"):
                    file_path = os.path.join(root, file_name)
                    # Try to extract date from filename, assuming YYYY-MM-DD.md format
                    try:
                        file_date_str = os.path.splitext(file_name)[0]
                        # Validate date format
                        datetime.strptime(file_date_str, '%Y-%m-%d')
                        is_valid_date_file = True
                    except ValueError:
                        is_valid_date_file = False
                        print(f"\nSkipping API checks for non-date file: {file_path}")
                        continue # Skip files not matching the date format

                    print(f"\nChecking API data for: {file_path}")
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

                    # Check and fetch Billboard (only if filename is a valid date)
                    billboard_heading = "## Billboard Hot 100"
                    if not file_handler.file_contains_section(file_path, billboard_heading):
                        # Date already validated above
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
                    else:
                        print(f"  Billboard section already exists.")

                    if needs_update:
                        processed_api_files += 1

        print(f"Finished processing API data. Updated {processed_api_files} file(s).")

    # --- Process Music History ---
    print(f"\n--- Processing Music History for files in {target_dir} ---")
    # Check if Apple Music file path is specified in config
    apple_music_file_path = config.get("APPLE_MUSIC_FILE_PATH")
    if not apple_music_file_path:
        print("WARNING: APPLE_MUSIC_FILE_PATH is not set. Skipping Apple Music history processing.")
    else:
        music_processor = MusicHistoryProcessor(config)
        music_processor.append_tracks_to_files()
        print("Music history processing complete.")

    # --- Process Netflix History ---
    print(f"\n--- Processing Netflix History (will create files if needed) ---")
    # Only process if password was provided AND download succeeded
    if netflix_password and download_succeeded:
        print("Proceeding with Netflix history processing...") # Added log
        try:
            netflix_processor = NetflixHistoryProcessor(config)
            # Pass True to delete the CSV file after processing
            processing_result = netflix_processor.append_shows_to_files(delete_after_processing=True)
            if processing_result:
                print("Netflix history processing complete. Original CSV file deleted if data was processed.")
            else:
                print("Netflix history processing completed with issues. CSV file may not have been deleted.")
        except Exception as e:
            print(f"ERROR processing Netflix history: {e}")
    elif not netflix_password:
        print("Skipping Netflix history processing as password was not provided.")
    else: # Password provided but download failed
        print("Skipping Netflix history processing as download did not succeed.")
        
    # --- Process Fandango Purchase History ---
    print(f"\n--- Processing Fandango Purchase History ---")
    # Check if Fandango credentials are specified in config
    fandango_username = config.get("FANDANGO_USER_NAME")
    if not fandango_username:
        print("WARNING: FANDANGO_USER_NAME is not set. Skipping Fandango history processing.")
    else:
        # Get Fandango password
        fandango_password = config.get("FANDANGO_PASSWORD")
        if not fandango_password:
            fandango_password = getpass.getpass("Enter Fandango Password: ")
            
        if not fandango_password:
            print("Fandango password not provided. Skipping Fandango purchase history download.")
        else:
            print("Downloading Fandango purchase history...")
            try:
                fandango_download_succeeded = download_fandango_history(config, fandango_password)
                if fandango_download_succeeded:
                    print("Fandango purchase history downloaded successfully.")
                    # Process the downloaded Fandango purchase history file
                    try:
                        fandango_processor = FandangoHistoryProcessor(config)
                        fandango_processing_result = fandango_processor.append_purchases_to_files(delete_after_processing=True)
                        if fandango_processing_result == True:
                            print("Fandango purchase history processing complete. Original file deleted if data was processed.")
                        else:
                            # Get the specific reason why processing failed
                            if not fandango_processor.fandango_html_file or not os.path.exists(fandango_processor.fandango_html_file):
                                print("No Fandango purchase history file found to process.")
                            elif hasattr(fandango_processor, 'last_error') and fandango_processor.last_error:
                                print(f"Fandango processing failed: {fandango_processor.last_error}")
                            else:
                                print("No Fandango purchase history data was found in the downloaded file.")
                    except Exception as e:
                        print(f"ERROR processing Fandango purchase history: {e}")
                else:
                    print("Fandango download function completed but reported failure.")
            except Exception as e:
                print(f"ERROR during Fandango download call: {e}")

    # --- Process Yelp Reviews ---
    print(f"\n--- Processing Yelp Reviews ---")
    yelp_html_path = config.get("YELP_USER_REVIEWS_HTML")
    if not yelp_html_path:
        print("WARNING: YELP_USER_REVIEWS_HTML is not set. Skipping Yelp review processing.")
    else:
        try:
            yelp_processor = YelpReviewProcessor(config)
            yelp_processor.append_reviews_to_files()
            print("Yelp review processing complete.")
        except Exception as e:
            print(f"ERROR processing Yelp reviews: {e}")
            
    # --- Process Ticketmaster Events ---
    print(f"\n--- Processing Ticketmaster Events ---")
    ticketmaster_csv_path = config.get("TICKET_MASTER_CSV_FILE")
    if not ticketmaster_csv_path or ticketmaster_csv_path.strip() == "":
        print("WARNING: TICKET_MASTER_CSV_FILE is not set or empty. Skipping Ticketmaster event processing.")
    else:
        try:
            if not os.path.exists(ticketmaster_csv_path):
                print(f"ERROR: Ticketmaster CSV file not found at {ticketmaster_csv_path}")
            else:
                ticketmaster_processor = TicketmasterProcessor(config)
                ticketmaster_processor.append_events_to_files()
                print("Ticketmaster event processing complete.")
        except Exception as e:
            print(f"ERROR processing Ticketmaster events: {e}")

    print("\nAll processing complete.")

if __name__ == "__main__":
    main()