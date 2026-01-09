"""
Proxy manager: load, scrape, validate, and select working proxies.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import requests

from .scraper import scrape_proxies_to_file
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProxyRecord:
    address: str
    proxy_type: str  # "http" or "socks5"
    alive: bool = False


class ProxyManager:
    """
    Handles loading, scraping, validating, and selecting proxies.
    """

    def __init__(
        self,
        proxy_type: str = "http",
        saved_file: str = "src/proxies/saved_proxies.txt",
        scrape_http_url: str = "",
        scrape_socks5_url: str = "",
    ) -> None:
        self.proxy_type = proxy_type
        self.saved_file = saved_file
        self.scrape_http_url = scrape_http_url
        self.scrape_socks5_url = scrape_socks5_url
        self.proxies: List[ProxyRecord] = []

    def load_saved_proxies(self, path: Optional[str] = None) -> List[ProxyRecord]:
        """
        Read IP:PORT lines from file and return list of ProxyRecord.
        """
        file_path = Path(path or self.saved_file)
        if not file_path.exists():
            logger.warning("Saved proxies file %s does not exist.", file_path)
            return []

        records: List[ProxyRecord] = []
        for line in file_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            records.append(ProxyRecord(address=line, proxy_type=self.proxy_type))
        self.proxies = records
        logger.info("Loaded %d proxies from %s", len(records), file_path)
        return records

    def scrape_proxies(self) -> List[ProxyRecord]:
        """
        Scrape proxies from GitHub based on proxy_type and load them.
        """
        if self.proxy_type == "http":
            url = self.scrape_http_url
            dest = "src/proxies/scraped_http.txt"
        else:
            url = self.scrape_socks5_url
            dest = "src/proxies/scraped_socks5.txt"

        scrape_proxies_to_file(url, dest)
        return self.load_saved_proxies(dest)

    def validate_proxy(self, proxy: ProxyRecord, timeout: int = 5) -> bool:
        """
        Quick HEAD request to httpbin.org/ip through the proxy to check liveness.
        """
        scheme = proxy.proxy_type
        proxy_url = f"{scheme}://{proxy.address}"
        proxies = {"http": proxy_url, "https": proxy_url}
        try:
            logger.debug("Validating proxy %s", proxy.address)
            resp = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=timeout)
            proxy.alive = resp.ok
        except requests.RequestException:
            proxy.alive = False
        return proxy.alive

    def get_working_proxy(self, n: int = 1) -> List[ProxyRecord]:
        """
        Return up to n validated proxy entries or empty list if none.
        """
        working: List[ProxyRecord] = []
        for proxy in self.proxies:
            if len(working) >= n:
                break
            if self.validate_proxy(proxy):
                working.append(proxy)
        logger.info("Found %d working proxies.", len(working))
        return working