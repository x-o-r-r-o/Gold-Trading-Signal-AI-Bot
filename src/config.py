from dataclasses import dataclass
from typing import Optional
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # Core
    twelvedata_api_key: str
    serpapi_key: Optional[str] = None
    perplexity_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Proxies
    use_proxies: bool = False
    proxy_mode: str = "load_saved"  # or "scrape"
    proxy_type: str = "http"
    saved_proxies_file: str = "src/proxies/saved_proxies.txt"

    # Perplexity / ChatGPT
    prefer_perplexity: bool = True
    use_chatgpt_for_prompt_refinement: bool = True

    # Output
    output_dir: str = "outputs"
    dry_run: bool = False

    # Notifications
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: Optional[str] = None
    smtp_to: Optional[str] = None

    # ML
    use_ml_signal: bool = False
    ml_model_config_path: str = "models/model_config.yaml"
    ml_device: str = "cpu"
    ml_blend_alpha: float = 0.5


def load_settings_from_env() -> Settings:
    api_key = os.getenv("TWELVEDATA_API_KEY")
    if not api_key:
        raise RuntimeError("TWELVEDATA_API_KEY is required")

    return Settings(
        twelvedata_api_key=api_key,
        serpapi_key=os.getenv("SERPAPI_KEY"),
        perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        use_proxies=os.getenv("USE_PROXIES", "false").lower() == "true",
        proxy_mode=os.getenv("PROXY_MODE", "load_saved"),
        proxy_type=os.getenv("PROXY_TYPE", "http"),
        saved_proxies_file=os.getenv("SAVED_PROXIES_FILE", "src/proxies/saved_proxies.txt"),
        prefer_perplexity=os.getenv("PREFER_PERPLEXITY", "true").lower() == "true",
        use_chatgpt_for_prompt_refinement=os.getenv(
            "USE_CHATGPT_FOR_PROMPT_REFINEMENT", "true"
        ).lower()
        == "true",
        output_dir=os.getenv("OUTPUT_DIR", "outputs"),
        dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        smtp_host=os.getenv("SMTP_HOST"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=os.getenv("SMTP_USERNAME"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        smtp_from=os.getenv("SMTP_FROM"),
        smtp_to=os.getenv("SMTP_TO"),
        use_ml_signal=os.getenv("USE_ML_SIGNAL", "false").lower() == "true",
        ml_model_config_path=os.getenv("ML_MODEL_CONFIG_PATH", "models/model_config.yaml"),
        ml_device=os.getenv("ML_DEVICE", "cpu"),
        ml_blend_alpha=float(os.getenv("ML_BLEND_ALPHA", "0.5")),
    )