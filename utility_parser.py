from typing import List, Dict, Any

class UtilityParser:
    """
    Class for parsing API responses.
    """

    def parse_news(self, news_data: Dict[Any, Any]) -> List[Dict[str, str]]:
        """
        Parses news data to extract titles and links.

        Args:
            news_data (Dict[Any, Any]): The API response containing news articles.

        Returns:
            List[Dict[str, str]]: A list of dictionaries with 'title' and 'link' keys.
        """
        # The news data may have 'data' as the key for articles
        # print(news_data)
        if 'data' not in news_data:
            print("No 'data' key found in the response.")
            return []
        articles = news_data.get('data', [])
        # print(articles)
        if not articles:
            print("No articles found in the response.")
            return []
        parsed = []
        for article in articles:
            title = article.get('title', '')
            link = article.get('link', '')
            if title and link:
                parsed.append({'title': title, 'link': link})
        return parsed

    def parse_weather(self, weather_data: Dict[Any, Any]) -> List[Dict[str, Any]]:
        """
        Parses weather data to extract daily forecast information.

        Args:
            weather_data (Dict[Any, Any]): The API response containing weather forecast.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries with daily weather information.
        """
        print(f"Weather data structure: {list(weather_data.keys()) if isinstance(weather_data, dict) else 'Invalid data'}")
        
        if 'forecastDaily' not in weather_data or 'days' not in weather_data['forecastDaily']:
            print("ERROR: Required keys 'forecastDaily' or 'days' not found in weather data")
            if 'forecastDaily' in weather_data:
                print(f"forecastDaily keys: {list(weather_data['forecastDaily'].keys())}")
            return []
            
        days = weather_data['forecastDaily']['days']
        print(f"Found {len(days)} days in forecast data")
        
        if not days:
            print("No daily forecasts found in the response.")
            return []
            
        parsed = []
        for i, day in enumerate(days):
            forecast = {
                'day_number': i + 1,
                'forecastStart': day.get('forecastStart', ''),
                'temperatureMax': day.get('temperatureMax', ''),
                'temperatureMin': day.get('temperatureMin', '')
            }
            
            # Extract data from daytimeForecast
            daytime = day.get('daytimeForecast', {})
            if not daytime:
                print(f"WARNING: Day {i+1} missing daytimeForecast")
                
            forecast['conditionCode'] = daytime.get('conditionCode', '')
            forecast['precipitationChance'] = daytime.get('precipitationChance', 0)
            forecast['precipitationAmount'] = daytime.get('precipitationAmount', 0)
            forecast['windSpeed'] = daytime.get('windSpeed', 0)
            
            parsed.append(forecast)
        
        print(f"Successfully parsed {len(parsed)} weather days")
        return parsed