from dataclasses import dataclass
from typing import List, Dict, Any

from .feature_builder import (
    build_feature_dict,
    build_feature_vector,
    normalize_features,
)
from .ml_models import (
    load_model_config,
    load_signal_model,
    predict_signal_proba,
    decode_prediction,
)
from ..utils.logger import logger


@dataclass
class SignalResult:
    signal: str
    score: float
    confidence_pct: float
    reasons: List[str]
    suggested_action: str | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    ml_raw: dict | None = None


def generate_signal(
    latest_price: float,
    indicators: Dict[str, float],
    news_agg: Dict[str, Any],
    major_macro_flag: bool,
) -> SignalResult:
    """
    Simple rule-based signal using indicators + sentiment.
    """
    price = latest_price
    rsi = indicators.get("rsi14", 50.0)
    macd_hist = indicators.get("macd_hist", 0.0)
    trend_slope = indicators.get("trend_slope", 0.0)
    ma_cross_bullish = indicators.get("ma_cross_bullish", False)
    vol = indicators.get("volatility20", 0.0)
    atr = indicators.get("atr14", 0.0)

    news_score = news_agg.get("average_score", 0.0)

    # Technical score
    tech_score = 0.0
    if rsi < 30:
        tech_score += 0.3
    elif rsi > 70:
        tech_score -= 0.3

    if macd_hist > 0:
        tech_score += 0.2
    elif macd_hist < 0:
        tech_score -= 0.2

    if trend_slope > 0:
        tech_score += 0.2
    elif trend_slope < 0:
        tech_score -= 0.2

    if ma_cross_bullish:
        tech_score += 0.2
    else:
        tech_score -= 0.1

    tech_score = max(min(tech_score, 1.0), -1.0)

    # Sentiment score
    sent_score = news_score  # already in [-1,1]

    # Volatility penalty
    vol_penalty = min(vol / (price * 0.02) if price > 0 else 0.0, 1.0)
    vol_score = -0.3 * vol_penalty

    # Macro
    macro_score = 0.2 if major_macro_flag and news_score > 0 else 0.0
    if major_macro_flag and news_score < 0:
        macro_score -= 0.2

    S = 0.4 * tech_score + 0.35 * sent_score + 0.15 * vol_score + 0.1 * macro_score
    S = max(min(S, 1.0), -1.0)

    # Map S to label
    if S >= 0.35:
        label = "BUY"
    elif S <= -0.35:
        label = "SELL"
    elif -0.15 < S < 0.15:
        label = "UNPREDICTABLE"
    else:
        label = "HOLD"

    confidence_pct = abs(S) * 100.0

    reasons: List[str] = []
    reasons.append(f"Technical composite score={tech_score:.2f}")
    reasons.append(f"News sentiment score={sent_score:.2f}")
    reasons.append(f"Volatility penalty contribution={vol_score:.2f}")
    reasons.append(f"Macro contribution={macro_score:.2f}")
    reasons.append(f"Final rule-based score S={S:.3f} → {label}")

    # Simple SL/TP based on ATR
    sl = None
    tp = None
    if atr > 0 and price > 0:
        if label == "BUY":
            sl = price - 1.5 * atr
            tp = price + 2.5 * atr
        elif label == "SELL":
            sl = price + 1.5 * atr
            tp = price - 2.5 * atr

    suggested = None
    if label == "BUY":
        suggested = "Consider long XAU/USD with appropriate risk management."
    elif label == "SELL":
        suggested = "Consider short XAU/USD with appropriate risk management."
    elif label == "HOLD":
        suggested = "Consider staying in current positions; no strong edge."
    else:
        suggested = "Stay out; signal is unpredictable / low confidence."

    return SignalResult(
        signal=label,
        score=S,
        confidence_pct=confidence_pct,
        reasons=reasons,
        suggested_action=suggested,
        stop_loss=sl,
        take_profit=tp,
    )


_model_cache: Dict[str, Any] = {}


def _map_score_to_label(score: float) -> str:
    if score >= 0.35:
        return "BUY"
    elif score <= -0.35:
        return "SELL"
    elif -0.15 < score < 0.15:
        return "UNPREDICTABLE"
    else:
        return "HOLD"


def _compute_confidence_from_score(score: float) -> float:
    return abs(score) * 100.0


def _load_ml_artifacts_once(config_path: str, device: str):
    cache_key = f"{config_path}::{device}"
    if cache_key in _model_cache:
        entry = _model_cache[cache_key]
        return entry["config"], entry["model"], entry["device"]

    cfg = load_model_config(config_path)
    model, used_device = load_signal_model(cfg, override_device=device)
    _model_cache[cache_key] = {"config": cfg, "model": model, "device": used_device}
    return cfg, model, used_device


def generate_signal_with_ml(
    latest_price: float,
    indicators: Dict[str, float],
    news_agg: Dict[str, Any],
    major_macro_flag: bool,
    settings,
) -> SignalResult:
    rule_res = generate_signal(
        latest_price=latest_price,
        indicators=indicators,
        news_agg=news_agg,
        major_macro_flag=major_macro_flag,
    )

    if not getattr(settings, "use_ml_signal", False):
        return rule_res

    config_path = getattr(settings, "ml_model_config_path", "models/model_config.yaml")
    ml_device = getattr(settings, "ml_device", "cpu")

    try:
        cfg, model, used_device = _load_ml_artifacts_once(config_path, ml_device)
    except Exception as e:
        logger.warning(f"[ML] Failed to load ML model/config: {e}. Falling back to rule-based.")
        return rule_res

    features_cfg = cfg.get("features", {}) or {}
    feature_order = features_cfg.get("order", []) or []
    normalization_cfg = features_cfg.get("normalization", {}) or {}

    try:
        feature_dict = build_feature_dict(
            latest_price=latest_price,
            indicators=indicators,
            news_agg=news_agg,
            major_macro_flag=major_macro_flag,
        )
        raw_vec = build_feature_vector(feature_dict, feature_order)
        norm_vec = normalize_features(raw_vec, feature_order, normalization_cfg)
    except Exception as e:
        logger.warning(f"[ML] Failed to build/normalize features: {e}. Falling back to rule-based.")
        return rule_res

    try:
        probs = predict_signal_proba(model, used_device, norm_vec)
        ml_pred = decode_prediction(probs, cfg)
    except Exception as e:
        logger.warning(f"[ML] Inference error: {e}. Falling back to rule-based.")
        return rule_res

    S_ml = float(ml_pred.get("pred_score", 0.0) or 0.0)
    ml_confidence = float(ml_pred.get("confidence", 0.0) or 0.0)

    alpha = float(getattr(settings, "ml_blend_alpha", 0.5) or 0.5)
    alpha = min(max(alpha, 0.0), 1.0)

    S_rule = float(rule_res.score or 0.0)
    S_final = alpha * S_rule + (1.0 - alpha) * S_ml

    final_label = _map_score_to_label(S_final)
    final_conf_pct = _compute_confidence_from_score(S_final)

    final_reasons = list(rule_res.reasons or [])
    ml_reason = (
        f"ML model suggests {ml_pred['pred_label']} "
        f"(probs SELL/HOLD/BUY = "
        f"{ml_pred['probs'][0]:.2f}/"
        f"{ml_pred['probs'][1]:.2f}/"
        f"{ml_pred['probs'][2]:.2f}, "
        f"ML confidence ≈ {ml_confidence * 100:.1f}%). "
        f"Blended score S_final={S_final:.3f} from S_rule={S_rule:.3f} and S_ml={S_ml:.3f} "
        f"with α={alpha:.2f}."
    )
    final_reasons.append(ml_reason)

    return SignalResult(
        signal=final_label,
        score=S_final,
        confidence_pct=final_conf_pct,
        reasons=final_reasons,
        suggested_action=rule_res.suggested_action,
        stop_loss=rule_res.stop_loss,
        take_profit=rule_res.take_profit,
        ml_raw=ml_pred,
    )