import requests
from typing import Optional, Dict, Any

class HttpSession:
    def __init__(self, proxies: Optional[Dict[str, str]] = None, timeout: int = 15):
        self.session = requests.Session()
        self.session.proxies = proxies or {}
        self.timeout = timeout

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, **kwargs):
        return self.session.get(url, params=params, timeout=self.timeout, **kwargs)

    def post(self, url: str, json: Optional[Dict[str, Any]] = None, **kwargs):
        return self.session.post(url, json=json, timeout=self.timeout, **kwargs)