from typing import List, Dict
import numpy as np


def compute_sma(series: np.ndarray, window: int) -> float:
    if len(series) < window:
        return float(series.mean())
    return float(series[-window:].mean())


def compute_ema(series: np.ndarray, window: int) -> float:
    if len(series) < window:
        window = len(series)
    alpha = 2 / (window + 1)
    ema = series[0]
    for x in series[1:]:
        ema = alpha * x + (1 - alpha) * ema
    return float(ema)


def compute_rsi(series: np.ndarray, window: int = 14) -> float:
    if len(series) < window + 1:
        return 50.0
    deltas = np.diff(series)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = gains[-window:].mean()
    avg_loss = losses[-window:].mean() if losses[-window:].mean() != 0 else 1e-9
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)


def compute_macd(series: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9):
    if len(series) < slow + signal:
        series = np.pad(series, (slow + signal - len(series), 0), mode="edge")

    ema_fast = compute_ema(series, fast)
    ema_slow = compute_ema(series, slow)
    macd_line = ema_fast - ema_slow
    # For simplicity, treat signal line as EMA over last N macd_line values (approx)
    # In production you'd compute full series; this is simplified.
    signal_line = macd_line  # placeholder
    hist = macd_line - signal_line
    return float(macd_line), float(signal_line), float(hist)


def compute_atr(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, window: int = 14) -> float:
    if len(closes) < window + 1:
        return float((highs - lows).mean())
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        trs.append(tr)
    atr = np.mean(trs[-window:])
    return float(atr)


def compute_indicators(closes: List[float], highs: List[float], lows: List[float]) -> Dict[str, float]:
    c = np.array(closes, dtype=float)
    h = np.array(highs, dtype=float)
    l = np.array(lows, dtype=float)

    sma20 = compute_sma(c, 20)
    ema50 = compute_ema(c, 50)
    rsi14 = compute_rsi(c, 14)
    macd_line, macd_signal, macd_hist = compute_macd(c)
    atr14 = compute_atr(h, l, c, 14)
    vol20 = float(np.std(c[-20:])) if len(c) >= 20 else float(np.std(c))

    ma_cross_bullish = sma20 > ema50

    # Trend slope via simple linear regression over last 20 closes
    if len(c) >= 20:
        y = c[-20:]
        x = np.arange(len(y))
        A = np.vstack([x, np.ones(len(x))]).T
        slope, _ = np.linalg.lstsq(A, y, rcond=None)[0]
    else:
        slope = 0.0

    return {
        "sma20": sma20,
        "ema50": ema50,
        "rsi14": rsi14,
        "macd_line": macd_line,
        "macd_signal": macd_signal,
        "macd_hist": macd_hist,
        "atr14": atr14,
        "volatility20": vol20,
        "ma_cross_bullish": ma_cross_bullish,
        "trend_slope": float(slope),
    }