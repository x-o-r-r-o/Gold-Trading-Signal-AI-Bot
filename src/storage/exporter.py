from pathlib import Path
from datetime import datetime
import csv
from typing import Any

from ..config import Settings
from ..collector.market import MarketData
from ..analyzer.signal_generator import SignalResult


def export_daily(
    settings: Settings,
    market_data: MarketData,
    news_agg: dict,
    signal_res: SignalResult,
):
    out_dir = Path(settings.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.utcnow().strftime("%Y%m%d")
    csv_path = out_dir / f"daily_{date_str}_XAUUSD.csv"
    txt_path = out_dir / f"daily_{date_str}_XAUUSD.txt"
    log_path = out_dir / "signal.txt"

    # CSV append
    header = [
        "timestamp",
        "symbol",
        "price",
        "signal",
        "score",
        "confidence_pct",
    ]
    row = [
        datetime.utcnow().isoformat(),
        "XAU/USD",
        market_data.latest_price,
        signal_res.signal,
        f"{signal_res.score:.4f}",
        f"{signal_res.confidence_pct:.1f}",
    ]
    file_exists = csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(header)
        writer.writerow(row)

    # Text report
    with txt_path.open("w", encoding="utf-8") as f:
        f.write(f"Timestamp: {datetime.utcnow().isoformat()} UTC\n")
        f.write(f"Symbol: XAU/USD\n")
        f.write(f"Price: {market_data.latest_price}\n")
        f.write(f"Signal: {signal_res.signal}\n")
        f.write(f"Score: {signal_res.score:.3f}\n")
        f.write(f"Confidence: {signal_res.confidence_pct:.1f}%\n")
        f.write("\nReasons:\n")
        for r in signal_res.reasons:
            f.write(f"- {r}\n")
        if signal_res.suggested_action:
            f.write(f"\nSuggested action: {signal_res.suggested_action}\n")
        if signal_res.stop_loss is not None:
            f.write(f"Stop-loss: {signal_res.stop_loss:.2f}\n")
        if signal_res.take_profit is not None:
            f.write(f"Take-profit: {signal_res.take_profit:.2f}\n")

    # Log line
    with log_path.open("a", encoding="utf-8") as f:
        f.write(
            f"{datetime.utcnow().isoformat()}\tXAU/USD\t"
            f"{signal_res.signal}\t{signal_res.score:.4f}\t"
            f"{signal_res.confidence_pct:.1f}\n"
        )