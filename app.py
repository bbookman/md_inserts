import json
from file_handler import FILE_HANDLER
from file_append_util import Append
from fetcher import fetch_and_process_api_data

def load_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Load config
    config = load_config('config.json')
    
    # Process news data
    news_markdown = fetch_and_process_api_data("NEWS", config)
    
    # Process weather data
    weather_markdown = fetch_and_process_api_data("WEATHER", config)
    
    # Get yesterday's file path
    file_handler = FILE_HANDLER()
    yesterday_file = file_handler.get_yesturday_file()
    
    if yesterday_file:
        # Append the markdown to the file
        append_util = Append()
        append_util.append_to_file(yesterday_file, news_markdown)
        append_util.append_to_file(yesterday_file, weather_markdown)
        print(f"Successfully appended data to {yesterday_file}")
    else:
        print("Yesterday's file not found")

if __name__ == "__main__":
    main()