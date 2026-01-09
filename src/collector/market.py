from dataclasses import dataclass
from typing import Dict
import requests

from ..config import Settings
from ..utils.logger import logger
from ..analyzer.technicals import compute_indicators


@dataclass
class MarketData:
    latest_price: float
    indicators: Dict[str, float]


def collect_market_data(settings: Settings) -> MarketData:
    api_key = settings.twelvedata_api_key
    symbol = "XAU/USD"
    base_url = "https://api.twelvedata.com"

    # Latest price
    price_resp = requests.get(
        f"{base_url}/price",
        params={"symbol": symbol, "apikey": api_key},
        timeout=15,
    )
    price_resp.raise_for_status()
    price_json = price_resp.json()
    latest_price = float(price_json["price"])

    # Time series for indicators
    ts_resp = requests.get(
        f"{base_url}/time_series",
        params={
            "symbol": symbol,
            "interval": "1day",
            "outputsize": 120,
            "apikey": api_key,
        },
        timeout=15,
    )
    ts_resp.raise_for_status()
    ts_json = ts_resp.json()
    values = ts_json["values"]

    closes = [float(bar["close"]) for bar in reversed(values)]
    highs = [float(bar["high"]) for bar in reversed(values)]
    lows = [float(bar["low"]) for bar in reversed(values)]

    indicators = compute_indicators(closes, highs, lows)

    logger.info(f"Latest XAU/USD price: {latest_price}")
    return MarketData(latest_price=latest_price, indicators=indicators)