from typing import Optional
import smtplib
from email.message import EmailMessage
import requests

from .config import Settings
from .collector.market import MarketData
from .analyzer.signal_generator import SignalResult
from .utils.logger import logger


def _build_message(signal_res: SignalResult, market_data: MarketData) -> str:
    lines = [
        f"Signal: {signal_res.signal}",
        f"Score: {signal_res.score:.3f}",
        f"Confidence: {signal_res.confidence_pct:.1f}%",
        f"Price: {market_data.latest_price}",
        "",
        "Reasons:",
    ]
    lines.extend(f"- {r}" for r in signal_res.reasons)
    if signal_res.suggested_action:
        lines.append("")
        lines.append(f"Suggested: {signal_res.suggested_action}")
    if signal_res.stop_loss is not None:
        lines.append(f"Stop-loss: {signal_res.stop_loss:.2f}")
    if signal_res.take_profit is not None:
        lines.append(f"Take-profit: {signal_res.take_profit:.2f}")
    return "\n".join(lines)


def _send_telegram(settings: Settings, text: str):
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        resp = requests.post(url, data={"chat_id": settings.telegram_chat_id, "text": text})
        resp.raise_for_status()
    except Exception as e:
        logger.warning(f"Failed to send Telegram message: {e}")


def _send_email(settings: Settings, text: str):
    if not settings.smtp_host or not settings.smtp_from or not settings.smtp_to:
        return

    msg = EmailMessage()
    msg["Subject"] = "Gold Signal Bot Alert"
    msg["From"] = settings.smtp_from
    msg["To"] = settings.smtp_to
    msg.set_content(text)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_username and settings.smtp_password:
                server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
    except Exception as e:
        logger.warning(f"Failed to send email: {e}")


def maybe_send_notifications(settings: Settings, signal_res: SignalResult, market_data: MarketData):
    text = _build_message(signal_res, market_data)
    _send_telegram(settings, text)
    _send_email(settings, text)