from typing import Dict, List


def build_feature_dict(
    latest_price: float,
    indicators: Dict[str, float],
    news_agg: Dict,
    major_macro_flag: bool,
) -> Dict[str, float]:
    price = float(latest_price) if latest_price is not None else 0.0

    sma20 = float(indicators.get("sma20", 0.0) or 0.0)
    ema50 = float(indicators.get("ema50", 0.0) or 0.0)
    rsi14 = float(indicators.get("rsi14", 0.0) or 0.0)
    macd_hist = float(indicators.get("macd_hist", 0.0) or 0.0)
    atr14 = float(indicators.get("atr14", 0.0) or 0.0)
    volatility20 = float(indicators.get("volatility20", 0.0) or 0.0)
    ma_cross_bullish_raw = indicators.get("ma_cross_bullish", False)
    trend_slope = float(indicators.get("trend_slope", 0.0) or 0.0)

    price_safe = price if price != 0.0 else 1.0

    sma20_over_price = sma20 / price_safe
    ema50_over_price = ema50 / price_safe
    atr14_over_price = atr14 / price_safe
    volatility20_over_price = volatility20 / price_safe
    trend_slope_over_price = trend_slope / price_safe

    ma_cross_bullish = 1.0 if bool(ma_cross_bullish_raw) else 0.0

    news_items = news_agg.get("items", []) or []
    news_sentiment = float(news_agg.get("average_score", 0.0) or 0.0)
    num_news_items = float(len(news_items))

    num_high_impact_pos = 0.0
    num_high_impact_neg = 0.0

    for item in news_items:
        impact_tag = (item.get("impact_tag") or "").lower()
        score = float(item.get("sentiment_score", 0.0) or 0.0)
        if impact_tag == "high":
            if score > 0:
                num_high_impact_pos += 1.0
            elif score < 0:
                num_high_impact_neg += 1.0

    macro_flag_val = 1.0 if major_macro_flag else 0.0

    return {
        "price": price,
        "sma20_over_price": sma20_over_price,
        "ema50_over_price": ema50_over_price,
        "rsi14": rsi14,
        "macd_hist": macd_hist,
        "atr14_over_price": atr14_over_price,
        "volatility20_over_price": volatility20_over_price,
        "ma_cross_bullish": ma_cross_bullish,
        "trend_slope_over_price": trend_slope_over_price,
        "news_sentiment": news_sentiment,
        "num_news_items": num_news_items,
        "num_high_impact_pos": num_high_impact_pos,
        "num_high_impact_neg": num_high_impact_neg,
        "macro_flag": macro_flag_val,
    }


def build_feature_vector(
    feature_dict: Dict[str, float],
    feature_order: List[str],
) -> List[float]:
    vector: List[float] = []
    for name in feature_order:
        value = float(feature_dict.get(name, 0.0) or 0.0)
        vector.append(value)
    return vector


def normalize_features(
    raw_vector: List[float],
    feature_order: List[str],
    normalization_cfg: Dict,
) -> List[float]:
    scheme = (normalization_cfg or {}).get("scheme", "none").lower()
    if scheme == "none":
        return list(raw_vector)

    if scheme != "standard":
        return list(raw_vector)

    mean_map = (normalization_cfg or {}).get("mean", {}) or {}
    std_map = (normalization_cfg or {}).get("std", {}) or {}

    normalized: List[float] = []
    for i, name in enumerate(feature_order):
        x = raw_vector[i]
        mean = float(mean_map.get(name, 0.0) or 0.0)
        std = float(std_map.get(name, 1.0) or 1.0)
        if std == 0.0:
            std = 1.0
        x_norm = (x - mean) / std
        normalized.append(x_norm)

    return normalized