import json
from api_util import make_api_request
from utility_parser import UtilityParser
from markdown_generator import Markdown
from file_handler import FILE_HANDLER
from file_append_util import Append

def load_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Load config
    config = load_config('config.json')
    news_endpoint = config.get('NEWS_ENDPOINT')
    news_key = config.get('NEWS_KEY')

    # Define parameters
    params = {
        'country': 'US',
        'lang': 'en',
        'limit': 5
    }

    # Call the news API
    news_data = make_api_request(news_key, news_endpoint, params)

    # Parse the response
    parser = UtilityParser()
    parsed_news = parser.parse_news(news_data)

    # Generate markdown from parsed news
    markdown_generator = Markdown()
    news_markdown = markdown_generator.generate_news_markdown(parsed_news)

    # Get yesterday's file path
    file_handler = FILE_HANDLER()
    yesterday_file = file_handler.get_yesturday_file()
    
    if yesterday_file:
        # Append the markdown to the file
        append_util = Append()
        append_util.append_to_file(yesterday_file, news_markdown)
        print(f"Successfully appended news to {yesterday_file}")
    else:
        print("Yesterday's file not found")

if __name__ == "__main__":
    main()