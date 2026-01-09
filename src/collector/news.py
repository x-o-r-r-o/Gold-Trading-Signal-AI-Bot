from typing import List, Dict, Any
import json
from datetime import datetime
from pathlib import Path

from ..config import Settings
from ..utils.logger import logger
from .google_search import search_news_with_serpapi


def collect_news_items(settings: Settings) -> List[Dict[str, Any]]:
    """
    Collect news via Perplexity (TODO) or SerpApi fallback.
    """
    # TODO: implement real Perplexity API call if PERPLEXITY_API_KEY is set.
    # For now, always use SerpApi.
    news_items = search_news_with_serpapi(settings)

    # Save raw news for audit
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(settings.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"news_{ts}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(news_items, f, ensure_ascii=False, indent=2)

    logger.info(f"Collected {len(news_items)} news items.")
    return news_items