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
        Generates markdown content from parsed Billboard data as a table.

        Args:
            billboard_items (List[Dict[str, str]]): List of song items with song details
            override_date: Optional date to use in the heading instead of chart date

        Returns:
            str: Markdown formatted table of Billboard Hot 100 songs.
        """
        if not billboard_items:
            return "No Billboard data found"

        # Get the chart date from the first item or use override date
        chart_date = override_date or billboard_items[0].get('date', datetime.now().strftime("%Y-%m-%d"))
        
        # Start with a new line for spacing
        markdown = "\n## Billboard Hot 100 - {}\n\n".format(chart_date)
        
        # Create table headers
        markdown += "| Song | Artist | Position |\n"
        markdown += "|------|--------|----------|\n"
        
        # Add each song as a row
        for i, song in enumerate(billboard_items):
            title = song.get('title', 'Unknown Title')
            artist = song.get('artist', 'Unknown Artist')
            position = i + 1  # Chart position is the index + 1
            weeks_at_no1 = song.get('weeks_at_no1', '0')
            weeks_on_chart = song.get('weeks_on_chart', '0')
            
            # Create position description
            position_text = f"#{position}"
            if position == 1 and weeks_at_no1 != '0':
                position_text += f" ({weeks_at_no1} weeks at #1, {weeks_on_chart} weeks on chart)"
            else:
                position_text += f" ({weeks_on_chart} weeks on chart)"
            
            # Add the row to the table
            markdown += f"| **{title}** | *{artist}* | {position_text} |\n"
        
        return markdown
    
    def generate_movies_attended_markdown(self, movie_items: List[Dict[str, str]]) -> str:
        """
        Generates markdown content for movies attended at theaters.
        
        Args:
            movie_items (List[Dict[str, str]]): List of movie items with 'movie_name', 'theater_name', 
                                               and 'theater_address' keys.
        
        Returns:
            str: Markdown formatted list of movies attended.
        """
        if not movie_items:
            return "No movie attendance data found"
            
        # Start with the header
        markdown = "\n## Movies Attended\n\n"
        
        # Add each movie as a bullet point with theater info
        for movie in movie_items:
            movie_name = movie.get('movie_name', 'Unknown Movie')
            theater_name = movie.get('theater_name', '')
            theater_address = movie.get('theater_address', '')
            
            # Format the entry with theater and address if available
            entry = f"* {movie_name}"
            
            if theater_name:
                entry += f" at {theater_name}"
                if theater_address:
                    entry += f" ({theater_address})"
            
            markdown += f"{entry}\n"
        
        return markdown