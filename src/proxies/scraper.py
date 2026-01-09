"""
Proxy list scraper.

Downloads raw proxy lists from GitHub and saves them to local files.
"""

from pathlib import Path
import requests
from ..utils.logger import get_logger

logger = get_logger(__name__)


def scrape_proxies_to_file(url: str, dest_path: str) -> None:
    """
    Download a proxy list from URL and save to dest_path.

    :param url: URL of raw list where each line is IP:PORT
    :param dest_path: Path to save the list.
    """
    logger.info("Scraping proxies from %s", url)
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    Path(dest_path).write_text(resp.text, encoding="utf-8")
    logger.info("Saved proxies to %s", dest_path)