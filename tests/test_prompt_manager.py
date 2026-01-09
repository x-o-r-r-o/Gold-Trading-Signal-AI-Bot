import os
import pytest
from src.prompt_manager import save_prompt, create_chatgpt_prompt_for_perplexity


@pytest.mark.unit
def test_save_prompt(tmp_path, monkeypatch):
    prompts_dir = tmp_path / "prompts"
    path = save_prompt("hello world", "testmeta", prompts_dir=str(prompts_dir))
    assert prompts_dir.exists()
    assert "hello world" in open(path, encoding="utf-8").read()


@pytest.mark.unit
def test_create_chatgpt_prompt_without_key(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    perplexity_prompt = create_chatgpt_prompt_for_perplexity(
        context=None, prompts_dir=str(tmp_path), openai_api_key=None
    )
    assert "Search the web for news in the last 48 hours" in perplexity_prompt