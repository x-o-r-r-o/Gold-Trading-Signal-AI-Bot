import os
import pytest

from src.collector.market import collect_market_data


@pytest.mark.liveapi
def test_collect_market_data_live():
    """
    Production-ready live test hitting Twelve Data.

    Requires TWELVEDATA_API_KEY in environment.
    """
    api_key = os.getenv("TWELVEDATA_API_KEY")
    if not api_key:
        pytest.skip("TWELVEDATA_API_KEY not set; skipping live test.")
    market = collect_market_data(api_key=api_key)
    assert market.latest_price > 0
    assert not market.ohlcv.empty
    assert "sma20" in market.indicators