import json
from api_util import make_api_request
from parser import Parser

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
    parser = Parser()
    parsed_news = parser.parse_news(news_data)

    # Print the parsed output
    print(parsed_news)

if __name__ == "__main__":
    main()