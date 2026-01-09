import pytest
from src.analyzer.signal_generator import generate_signal


@pytest.mark.unit
def test_generate_signal_basic():
    res = generate_signal(
        latest_price=2000.0,
        indicators={
            "sma20": 1990.0,
            "ema50": 1980.0,
            "rsi14": 40.0,
            "macd_hist": 0.1,
            "atr14": 20.0,
            "volatility20": 15.0,
            "ma_cross_bullish": True,
            "trend_slope": 1.0,
        },
        news_agg={"average_score": 0.1, "items": []},
        major_macro_flag=False,
    )
    assert res.signal in {"BUY", "SELL", "HOLD", "UNPREDICTABLE"}
    assert -1.0 <= res.score <= 1.0
    assert 0.0 <= res.confidence_pct <= 100.0