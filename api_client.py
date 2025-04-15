import requests
from typing import Dict, Any, Optional
from api_util import make_api_request

class ApiClient:
    def __init__(self, api_key: str, endpoint: str):
        self.api_key = api_key
        self.endpoint = endpoint

    def get_news(self, params: Optional[Dict[str, Any]] = None) -> Dict[Any, Any]:
        """
        Retrieves news articles.
        """
        return make_api_request(self.api_key, self.endpoint, params)
