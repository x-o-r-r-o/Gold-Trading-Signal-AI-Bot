import argparse
from pathlib import Path

from .config import load_settings_from_env, Settings
from .utils.logger import logger
from .collector.market import collect_market_data
from .collector.news import collect_news_items
from .analyzer.sentiment import analyze_news_sentiment
from .analyzer.signal_generator import generate_signal_with_ml
from .storage.exporter import export_daily
from .notifications import maybe_send_notifications


def parse_args():
    parser = argparse.ArgumentParser(description="Gold Signal Bot")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--output-dir", type=str, default=None)

    # Proxies
    parser.add_argument("--use-proxies", action="store_true")
    parser.add_argument("--proxy-mode", choices=["load_saved", "scrape"], default=None)
    parser.add_argument("--proxy-type", choices=["http", "socks5"], default=None)

    # Perplexity / ChatGPT
    parser.add_argument("--prefer-perplexity", dest="prefer_perplexity", action="store_true")
    parser.add_argument("--no-prefer-perplexity", dest="prefer_perplexity", action="store_false")
    parser.set_defaults(prefer_perplexity=None)

    parser.add_argument(
        "--use-chatgpt-for-prompt-refinement",
        dest="use_chatgpt_for_prompt_refinement",
        action="store_true",
    )
    parser.add_argument(
        "--no-use-chatgpt-for-prompt-refinement",
        dest="use_chatgpt_for_prompt_refinement",
        action="store_false",
    )
    parser.set_defaults(use_chatgpt_for_prompt_refinement=None)

    parser.add_argument("--dry-run", action="store_true")

    # ML
    parser.add_argument("--use-ml-signal", dest="use_ml_signal", action="store_true")
    parser.add_argument("--no-use-ml-signal", dest="use_ml_signal", action="store_false")
    parser.set_defaults(use_ml_signal=None)

    parser.add_argument("--ml-model-config-path", type=str, default=None)
    parser.add_argument("--ml-device", choices=["cpu", "cuda"], default=None)
    parser.add_argument("--ml-blend-alpha", type=float, default=None)

    return parser.parse_args()


def apply_cli_overrides(settings: Settings, args) -> Settings:
    if args.output_dir:
        settings.output_dir = args.output_dir

    if args.use_proxies:
        settings.use_proxies = True
    if args.proxy_mode:
        settings.proxy_mode = args.proxy_mode
    if args.proxy_type:
        settings.proxy_type = args.proxy_type

    if args.prefer_perplexity is not None:
        settings.prefer_perplexity = args.prefer_perplexity
    if args.use_chatgpt_for_prompt_refinement is not None:
        settings.use_chatgpt_for_prompt_refinement = args.use_chatgpt_for_prompt_refinement

    if args.dry_run:
        settings.dry_run = True

    if args.use_ml_signal is not None:
        settings.use_ml_signal = args.use_ml_signal
    if args.ml_model_config_path:
        settings.ml_model_config_path = args.ml_model_config_path
    if args.ml_device:
        settings.ml_device = args.ml_device
    if args.ml_blend_alpha is not None:
        settings.ml_blend_alpha = args.ml_blend_alpha

    return settings


def run_once(settings: Settings):
    Path(settings.output_dir).mkdir(parents=True, exist_ok=True)

    logger.info("Collecting market data...")
    market_data = collect_market_data(settings)

    logger.info("Collecting news...")
    news_items = collect_news_items(settings)

    logger.info("Analyzing sentiment...")
    news_agg = analyze_news_sentiment(news_items)

    # For now, naive macro flag: true if any high-impact items
    major_macro_flag = any(
        (item.get("impact_tag") or "").lower() == "high" for item in news_items
    )

    logger.info("Generating signal (rule-based + optional ML)...")
    signal_res = generate_signal_with_ml(
        latest_price=market_data.latest_price,
        indicators=market_data.indicators,
        news_agg=news_agg,
        major_macro_flag=major_macro_flag,
        settings=settings,
    )

    logger.info(
        f"Final signal: {signal_res.signal} (score={signal_res.score:.3f}, "
        f"confidence={signal_res.confidence_pct:.1f}%)"
    )

    if not settings.dry_run:
        export_daily(settings, market_data, news_agg, signal_res)
        maybe_send_notifications(settings, signal_res, market_data)

    logger.info("Done.")


def main():
    args = parse_args()
    settings = load_settings_from_env()
    settings = apply_cli_overrides(settings, args)

    if args.once:
        run_once(settings)
    else:
        # For now, only once mode is implemented
        run_once(settings)


if __name__ == "__main__":
    main()