# MD Inserts

A utility for adding structured data and content to markdown files based on various data sources. This tool can be used to enrich markdown journals or notes with information from external sources.

## Features

### API Data Integration: Fetches and formats data from various Rapidapi endpoints including:

- News headlines
- Weather information
- Top box office movies
- Billboard Hot 100 music charts
- Fandango ticket purchases

### Content History File Processing: Inserts content history from:

- Your Netflix viewing history with automatic downloading. Requires EMAIL_ADDRESS, Currently prompts for password.
- Your Yelp reviews. Requires sending request to Yelp.
- Your Apple Music listening history. Requires sending request to Apple.

**See below for information on how to obtain the required files**

## Configuration

The application uses a `config.json` file to store all necessary configuration parameters:

```json
{
  "NEWS_ENDPOINT": "https://real-time-news-data.p.rapidapi.com/top-headlines",
  "TARGET_DIR": "/path/to/your/markdown/files",
  "WEATHER_ENDPOINT": "https://easy-weather1.p.rapidapi.com/daily/5",
  "LATITUDE": "WEATHER LOCATION LATITUDE",
  "LONGITUDE": "WEATHER LOCATION LONGITUDE",
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
  "YELP_USER_REVIEWS_HTML": "/path/to/Yelp/html/user_review.html",
  "FANDANGO_USER_NAME": "",
  "FANDANGO_PASSWORD": ""
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
2. Process Apple music listening history, if provided
3. Download and process Netflix viewing history (if credentials provided)
4. Process Yelp review data, if provided

### File Format

The app specifically looks for files with names in the format `YYYY-MM-DD.md` (e.g., `2025-04-26.md`). Only files matching this date format will be processed. This allows the app to properly organize entries by date and match content to the appropriate date files.

## Behavior Notes

- If `RAPID_API_KEY` is not set, all API-based data retrieval will be skipped
- If specific API endpoints like `NEWS_ENDPOINT`, `WEATHER_ENDPOINT`, etc. are not set, those specific data sources will be skipped
- If Netflix configuration parameters (`NETFLIX_HISTORY_URL`, `EMAIL_ADDRESS`, or `NETFLIX_FILE_LOCATION`) are missing, Netflix data processing will be skipped
- Netflix history CSV files are automatically deleted after processing (configurable)

## Obtaining data

### Rapid API
1. Sign up for a RapidAPI account: Visit https://rapidapi.com/ and create an account.
2. Sign up for the basic service plan for any of the following:
   - [News](https://rapidapi.com/letscrape-6bRBa3QguO5/api/real-time-news-data)
   - [Weather](https://rapidapi.com/aptitudeapps/api/easy-weather1)
   - [Movies](https://rapidapi.com/apininjas/api/imdb236)
   - [Billboard](https://rapidapi.com/LDVIN/api/billboard-api)
3. API key:
     - Click Apps in the top right
     - In the left sidebar, click "My Apps"
     - Click the app that was auto generated.  Name might be "default-application_####"
     - Click Autorization
     - Click Add Key
     - Copy the key someplace safe.

### Apple Music

1. Go to Apple's privacy website: Visit privacy.apple.com.

2. Sign in with your Apple ID: You’ll need to log in using the credentials linked to your Apple Music account.

3. Request your data: Select "Request a copy of your data" and then choose "Apple Media Services information" to include your Apple Music listening history.

4. Submit the request: Apple will process your request, and once it's ready, they'll notify you via email with a link to download your data.

5. Once you receive the email and download the bundle, unzip the file and you'll find a CSV file named "Apple Music - Track Play History.csv".

It may take a few days for Apple to prepare the report, so keep an eye on your email for updates.

### Yelp reviews

1. Log in to Yelp: Visit www.yelp.com and sign in to your account.

2. Go to Privacy Settings: Navigate to Yelp’s Privacy Policy.

3. Request Your Data: Look for an option like "Request a copy of your personal data" or "Download your account history".

4. Submit Your Request: Follow the prompts to confirm your request. Yelp may take some time to process and email you the file with your post history.

5. Once you receive the email, download the file. Unzip. The required file is: Yelp/html/user_review.html
