from typing import List, Dict, Any
import requests
from ..config import Settings
from ..utils.logger import logger


def search_news_with_serpapi(settings: Settings) -> List[Dict[str, Any]]:
    """
    Basic SerpApi-based Google News search for gold-related headlines.
    """
    if not settings.serpapi_key:
        logger.warning("SERPAPI_KEY not set; returning empty news list.")
        return []

    url = "https://serpapi.com/search"
    params = {
        "engine": "google_news",
        "q": "gold price XAUUSD macro economic news",
        "api_key": settings.serpapi_key,
    }

    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    articles = data.get("news_results", []) or []
    items: List[Dict[str, Any]] = []

    for art in articles:
        title = art.get("title", "")
        summary = art.get("snippet", "")
        link = art.get("link", "")
        source = art.get("source", "")
        date_str = art.get("date", "")

        # naive impact tag
        impact_tag = "medium"
        text_lower = (title + " " + summary).lower()
        if any(k in text_lower for k in ["fed", "fomc", "cpi", "inflation", "rate hike"]):
            impact_tag = "high"

        items.append(
            {
                "title": title,
                "summary": summary,
                "url": link,
                "source": source,
                "pub_date": date_str,
                "excerpt": summary,
                "impact_tag": impact_tag,
            }
        )

    return items