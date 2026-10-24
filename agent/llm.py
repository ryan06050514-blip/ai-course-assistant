"""LLM 設定抽象化：同一份程式碼，靠環境變數切換本地與雲端模型。"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 讀取 repo 根目錄的 .env；不會覆蓋已存在的環境變數

PRESETS = {  # 預設值；實際以 .env 為準
    "local": ("http://localhost:11434/v1", "qwen3:1.7b"),
    "openai": ("https://api.openai.com/v1", "gpt-6-luna"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-3.8-flash"),
    "anthropic": ("https://api.anthropic.com/v1/", "claude-haiku-5-5"),
}


@dataclass
class LLM:
    profile: str
    client: OpenAI
    model: str


def get_llm(profile: str | None = None) -> LLM:
    profile = profile or os.getenv("LLM_PROFILE", "local")
    p = profile.upper()
    base, model = PRESETS.get(profile, PRESETS["local"])
    base = os.getenv(f"{p}_BASE_URL", os.getenv("LLM_BASE_URL", base))
    model = os.getenv(f"{p}_MODEL", os.getenv("LLM_MODEL", model))
    key = os.getenv(f"{p}_API_KEY", "ollama")  # Ollama 不驗 key
    return LLM(profile, OpenAI(base_url=base, api_key=key, timeout=120), model)


# 每百萬 token 的美元價格（2026-10 官方價目表；本地模型以 0 計）
PRICES = {
    "gpt-6-luna": (0.10, 0.50),
    "gpt-6.1-sol": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "gemini-3.1-pro-preview": (2.00, 12.00),
}


def cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    pin, pout = PRICES.get(model, (0.0, 0.0))
    return (prompt_tokens * pin + completion_tokens * pout) / 1_000_000
