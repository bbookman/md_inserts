# MD Inserts

A utility for adding structured data and content to markdown files based on various data sources. This tool can be used to enrich markdown journals or notes with information from external sources.

## Features

- **API Data Integration**: Fetches and formats data from various APIs including:

  - News headlines
  - Weather information
  - Top box office movies
  - Billboard Hot 100 music charts

- **Content History Processing**:
  - Apple Music listening history
  - Netflix viewing history with automatic downloading
  - Yelp reviews and activities

## Configuration

The application uses a `config.json` file to store all necessary configuration parameters:

```json
{
  "NEWS_ENDPOINT": "https://real-time-news-data.p.rapidapi.com/top-headlines",
  "TARGET_DIR": "/path/to/your/markdown/files",
  "WEATHER_ENDPOINT": "your-weather-endpoint",
  "LATITUDE": 34.2257,
  "LONGITUDE": -77.9447,
  "TOP_MOVIES_ENDPOINT": "https://imdb236.p.rapidapi.com/imdb/top-box-office",
  "BILLBOARD_ENDPOINT": "https://billboard-api2.p.rapidapi.com/hot-100",
  "NEWS_PARAMS": {
    "country": "US",
    "lang": "en",
    "limit": 5
  },
  "BILLBOARD_PARAMS": {
    "date": "",
    "range": "1-10"
  },
  "RAPID_API_KEY": "your-rapid-api-key",
  "APPLE_MUSIC_FILE_PATH": "/path/to/Apple Music - Track Play History.csv",
  "NETFLIX_HISTORY_URL": "https://www.netflix.com/viewingactivity",
  "EMAIL_ADDRESS": "your-email@example.com",
  "NETFLIX_FILE_LOCATION": "/path/to/download/netflix/data",
  "YELP_USER_REVIEWS_HTML": "/path/to/Yelp/html/user_review.html"
}
```

**Note:** `RAPID_API_KEY` is only required once as all the Rapid API services (News, Weather, Movies, Billboard) use the same API key. You don't need to configure separate API keys for each endpoint.

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure your `config.json` file with appropriate values
4. Prepare your data sources (API keys, CSV files, etc.)

## Usage

Run the main application:

```
python app.py
```

The application will:

1. Check and process API data for existing markdown files in the target directory
2. Process music listening history
3. Download and process Netflix viewing history (if credentials provided)
4. Process Yelp review data

### File Format

The app specifically looks for files with names in the format `YYYY-MM-DD.md` (e.g., `2025-04-26.md`). Only files matching this date format will be processed. This allows the app to properly organize entries by date and match content to the appropriate date files.

## Behavior Notes

- If `RAPID_API_KEY` is not set, all API-based data retrieval will be skipped
- If specific API endpoints like `NEWS_ENDPOINT`, `WEATHER_ENDPOINT`, etc. are not set, those specific data sources will be skipped
- If Netflix configuration parameters (`NETFLIX_HISTORY_URL`, `EMAIL_ADDRESS`, or `NETFLIX_FILE_LOCATION`) are missing, Netflix data processing will be skipped
- Netflix history CSV files are automatically deleted after processing (configurable)
- Apple Music history requires a CSV export file
- Yelp reviews require an HTML export file

## File Structure

- `app.py` - Main application entry point
- `api_util.py` - Utilities for API requests
- `fetcher.py` - Handles fetching data from APIs
- `file_handler.py` - Manages file operations
- `file_append_util.py` - Utilities for appending content to files
- `markdown_generator.py` - Generates formatted markdown from data
- `music_history.py` - Processes Apple Music history
- `netflix_downloader.py` - Downloads Netflix viewing history
- `netflix_history.py` - Processes Netflix viewing data
- `utility_parser.py` - Parses API responses
- `yelp_parser.py` - Processes Yelp review data

## Requirements

See `requirements.txt` for the complete list of dependencies.
