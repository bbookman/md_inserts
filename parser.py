from typing import List, Dict, Any

class Parser:
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