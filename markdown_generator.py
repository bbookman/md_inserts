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

        # Create the header with current date
        markdown = "## Tomorrow's News - {}\n\n".format(
            datetime.now().strftime("%Y-%m-%d")
        )

        # Add each news item as a markdown link
        for item in news_items:
            markdown += "- [{}]({})\n\n".format(item['title'], item['link'])

        return markdown