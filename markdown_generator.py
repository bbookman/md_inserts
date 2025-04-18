from typing import List, Dict
from datetime import datetime

class Markdown:
    """
    Class for generating markdown content from parsed data.
    """

    def generate_news_markdown(self, news_items: List[Dict[str, str]]) -> str:
        """
        Generates markdown content from parsed news data.

        Args:
            news_items (List[Dict[str, str]]): List of news items with 'title' and 'link' keys.

        Returns:
            str: Markdown formatted string of news items.
        """
        if not news_items:
            return "No news items found"

        # Start with a new line for spacing
        markdown = "\n## Tomorrow's News - {}\n\n".format(
            datetime.now().strftime("%Y-%m-%d")
        )

        # Add each news item as a markdown link
        for item in news_items:
            markdown += "- [{}]({})\n\n".format(item['title'], item['link'])

        return markdown

    def generate_weather_markdown(self, weather_items: List[Dict[str, any]]) -> str:
        """
        Generates markdown content from parsed weather data.

        Args:
            weather_items (List[Dict[str, any]]): List of weather forecasts with required keys.

        Returns:
            str: Markdown formatted table of weather forecast.
        """
        if not weather_items:
            return "No weather data found"

        # Start with a new line for spacing
        markdown = "\n## 5-Day Weather Forecast - {}\n\n".format(
            datetime.now().strftime("%Y-%m-%d")
        )
        
        # Start the table with weather attribute column
        markdown += "| Weather |"
        
        # Add column headers with dates
        for item in weather_items:
            # Parse and format the date as DD-MM-YYYY
            date_obj = datetime.fromisoformat(item['forecastStart'].replace('Z', '+00:00'))
            formatted_date = date_obj.strftime("%d-%m-%Y")
            markdown += f" {formatted_date} |"
        
        markdown += "\n|---------|" + "----------|" * len(weather_items) + "\n"
        
        # Add rows for each weather attribute
        attributes = [
            ('Conditions', 'conditionCode'),
            ('Max', 'temperatureMax'),
            ('Min', 'temperatureMin'),
            ('Chance of rain', 'precipitationChance'),
            ('Rain amount', 'precipitationAmount'),
            ('Wind', 'windSpeed')
        ]
        
        for display_name, attr_key in attributes:
            markdown += f"| {display_name} |"
            
            for item in weather_items:
                value = item.get(attr_key, '')
                
                # Format values appropriately
                if attr_key == 'temperatureMax' or attr_key == 'temperatureMin':
                    # Convert Celsius to Fahrenheit: F = C × 9/5 + 32
                    if value:
                        fahrenheit = (value * 9/5) + 32
                        formatted_value = f"{fahrenheit:.1f}°F"
                    else:
                        formatted_value = "N/A"
                elif attr_key == 'precipitationChance':
                    formatted_value = f"{int(value * 100)}%" if value else "0%"
                elif attr_key == 'precipitationAmount':
                    # Convert mm to inches (1 mm = 0.0393701 inches)
                    inches = value * 0.0393701 if value else 0
                    formatted_value = f"{inches:.2f}\"" if inches else "0\""
                elif attr_key == 'windSpeed':
                    # Convert km/h to mph (1 km/h = 0.621371 mph)
                    if value:
                        mph = value * 0.621371
                        formatted_value = f"{mph:.1f} mph"
                    else:
                        formatted_value = "N/A"
                else:
                    formatted_value = str(value)
                    
                markdown += f" {formatted_value} |"
            
            markdown += "\n"
        
        return markdown

    def generate_top_movies_markdown(self, movie_items: List[Dict[str, str]]) -> str:
        """
        Generates markdown content from parsed movie data.

        Args:
            movie_items (List[Dict[str, str]]): List of movie items with 'title', 'description', and 'image' keys.

        Returns:
            str: Markdown formatted table of top movies.
        """
        if not movie_items:
            return "No movie data found"

        # Start with a new line for spacing
        markdown = "\n## Top Movies - {}\n\n".format(
            datetime.now().strftime("%Y-%m-%d")
        )
        
        # Create table headers
        markdown += "| Title | Poster | Description |\n"
        markdown += "|-------|--------|-------------|\n"
        
        # Add each movie as a row
        for movie in movie_items:
            title = movie.get('title', 'Unknown Title')
            description = movie.get('description', 'No description available')
            image_url = movie.get('image', '')
            
            # Limit description length to avoid extremely long table cells
            if len(description) > 300:
                description = description[:297] + "..."
                
            # Create image markdown using HTML with reduced size (33%)
            if image_url:
                image_md = f'<img src="{image_url}" alt="{title}" width="33%" />'
            else:
                image_md = "No image available"
            
            # Add the row to the table
            markdown += f"| **{title}** | {image_md} | {description} |\n"
        
        return markdown

    def generate_billboard_markdown(self, billboard_items: List[Dict[str, str]], override_date=None) -> str:
        """
        Generates markdown content from parsed Billboard data.
        
        Args:
            billboard_items: List of song items
            override_date: Optional date to use in the heading instead of chart date
        """
        if not billboard_items:
            return "No Billboard data found"

        # Use override_date if provided, otherwise get from API response
        display_date = override_date or billboard_items[0].get('date', datetime.now().strftime("%Y-%m-%d"))
        
        markdown = f"\n## Billboard Hot 100 - {display_date}\n\n"
        
        # Create a numbered list of songs
        for i, song in enumerate(billboard_items):
            title = song.get('title', 'Unknown Title')
            artist = song.get('artist', 'Unknown Artist')
            weeks_on_chart = song.get('weeks_on_chart', '0')
            weeks_at_no1 = song.get('weeks_at_no1', '0')
            
            # Add weeks at #1 for the top song
            if i == 0 and weeks_at_no1 != '0':
                markdown += f"{i+1}. **{title}** by *{artist}* (#{1} for {weeks_at_no1} weeks, {weeks_on_chart} weeks on chart)\n"
            else:
                markdown += f"{i+1}. **{title}** by *{artist}* ({weeks_on_chart} weeks on chart)\n"
        
        return markdown