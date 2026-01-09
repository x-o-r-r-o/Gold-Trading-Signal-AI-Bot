"""
Prompt manager for ChatGPT and Perplexity prompts.

- create_chatgpt_prompt_for_perplexity(context)
- save_prompt(content, meta)
"""

from __future__ import annotations

from typing import Optional
from datetime import datetime
from pathlib import Path
import os

from openai import OpenAI

from .storage.persistence import timestamp_str, save_text, save_json
from .utils.logger import get_logger

logger = get_logger(__name__)


CHATGPT_TEMPLATE = (
    "You are a professional trader. Produce a concise Perplexity "
    "search prompt (1-3 sentences) that will retrieve high-quality, recent (last 48 hours) "
    "news and analysis relevant to XAU/USD (Gold) and macro drivers such as US CPI, Fed commentary, "
    "USD strength, inflation, ETF flows, and geopolitical risk. Instruct Perplexity to return a JSON array "
    "of up to 20 items with fields: title, summary (<=80 words), url, source, pub_date (ISO8601), excerpt, "
    "sentiment (POS/NEG/NEUTRAL), impact_tag (high/medium/low). Prefer Bloomberg, Reuters, FT, CNBC, "
    "recognized commodity analysts, and central bank releases. Keep the prompt strictly focused and "
    "provide no extraneous text."
)


def save_prompt(
    content: str,
    meta: str,
    prompts_dir: str = "prompts",
) -> str:
    """
    Save a prompt to prompts/prompt_{timestamp}_{meta}.txt.
    """
    ts = timestamp_str()
    filename = f"prompt_{ts}_{meta}.txt"
    path = Path(prompts_dir) / filename
    return save_text(str(path), content)


def create_chatgpt_prompt_for_perplexity(
    context: Optional[str],
    prompts_dir: str,
    openai_api_key: Optional[str],
) -> str:
    """
    Use ChatGPT to generate the Perplexity prompt text.

    Saves:
      - the ChatGPT prompt used
      - the ChatGPT output (Perplexity prompt text)
    """
    prompt_used = CHATGPT_TEMPLATE
    if context:
        prompt_used += "\n\nAdditional context:\n" + context

    prompt_file = save_prompt(prompt_used, meta="chatgpt", prompts_dir=prompts_dir)

    if not openai_api_key:
        logger.warning("OPENAI_API_KEY not set; returning default Perplexity prompt.")
        # Fallback: static Perplexity prompt from spec
        perplexity_prompt = (
            "[Search the web for news in the last 48 hours about XAU/USD (Gold), central bank "
            "policies affecting gold, USD strength and inflation data]. Return a JSON array (max 20) "
            "with fields: title, summary (<=80 words), url, source, pub_date (ISO8601), excerpt "
            "(one sentence), sentiment (POS/NEG/NEUTRAL), impact_tag (high/medium/low). Prefer Bloomberg, "
            "Reuters, Financial Times, CNBC, and credible commodity analysts. Include central bank statements, "
            "CPI/PPI releases, USD moves, ETF flows, and geopolitical events. Prioritize items with explicit "
            "price-impact claims."
        )
        perplexity_prompt_file = save_prompt(
            perplexity_prompt, meta="perplexity", prompts_dir=prompts_dir
        )
        return perplexity_prompt

    client = OpenAI(api_key=openai_api_key)
    logger.info("Calling OpenAI to generate Perplexity prompt.")
    resp = client.responses.create(
        model="gpt-4o-mini",
        input=prompt_used,
    )
    # Extract text (depends on new OpenAI client structure)
    try:
        content = resp.output[0].content[0].text
    except Exception:
        # fallback: try older-style data
        content = str(resp)

    perplexity_prompt = content.strip()
    perplexity_prompt_file = save_prompt(
        perplexity_prompt, meta="perplexity", prompts_dir=prompts_dir
    )

    return perplexity_prompt