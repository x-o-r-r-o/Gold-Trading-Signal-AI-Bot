import pytest
from src.analyzer.feature_builder import build_feature_dict, build_feature_vector


@pytest.mark.unit
def test_feature_builder_shape():
    feature_dict = build_feature_dict(
        latest_price=2000.0,
        indicators={
            "sma20": 1990.0,
            "ema50": 1980.0,
            "rsi14": 45.0,
            "macd_hist": 0.05,
            "atr14": 20.0,
            "volatility20": 10.0,
            "ma_cross_bullish": True,
            "trend_slope": 0.5,
        },
        news_agg={"average_score": 0.1, "items": []},
        major_macro_flag=False,
    )
    order = [
        "price",
        "sma20_over_price",
        "ema50_over_price",
        "rsi14",
        "macd_hist",
        "atr14_over_price",
        "volatility20_over_price",
        "ma_cross_bullish",
        "trend_slope_over_price",
        "news_sentiment",
        "num_news_items",
        "num_high_impact_pos",
        "num_high_impact_neg",
        "macro_flag",
    ]
    vec = build_feature_vector(feature_dict, order)
    assert len(vec) == 14