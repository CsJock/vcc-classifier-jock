import logging
from pathlib import Path

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

try:
    import anthropic
except ImportError:  # pragma: no cover
    anthropic = None


def _load_groq_key() -> str:
    direct = (settings.groq_api_key or "").strip()
    if direct:
        return direct

    key_file = (settings.groq_key_file or "").strip()
    if not key_file:
        return ""

    path = Path(key_file).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8").strip()


def _resolve_provider() -> tuple[str, str]:
    provider = (settings.llm_provider or "auto").strip().lower()
    anthropic_key = (settings.anthropic_api_key or "").strip()
    groq_key = _load_groq_key()

    if provider == "anthropic":
        if not anthropic_key:
            raise RuntimeError("LLM_PROVIDER=anthropic 但 ANTHROPIC_API_KEY 未設定")
        return "anthropic", anthropic_key

    if provider == "groq":
        if not groq_key:
            raise RuntimeError("LLM_PROVIDER=groq 但 GROQ_API_KEY/GROQ_KEY_FILE 未設定")
        return "groq", groq_key

    if provider == "auto":
        if anthropic_key:
            return "anthropic", anthropic_key
        if groq_key:
            return "groq", groq_key
        raise RuntimeError("未找到可用 LLM 金鑰（ANTHROPIC_API_KEY 或 GROQ_API_KEY/GROQ_KEY_FILE）")

    raise RuntimeError(f"不支援的 LLM_PROVIDER: {provider}")


def _pick_model(provider: str, tier: str) -> str:
    normalized = tier.strip().lower()
    if provider == "anthropic":
        if normalized == "strong":
            return settings.anthropic_model_strong
        return settings.anthropic_model_fast
    if normalized == "strong":
        return settings.groq_model_strong
    return settings.groq_model_fast


async def complete(
    *,
    system_prompt: str,
    user_prompt: str,
    tier: str = "fast",
    max_tokens: int = 4096,
) -> str:
    provider, key = _resolve_provider()
    model = _pick_model(provider, tier)

    if provider == "anthropic":
        if anthropic is None:  # pragma: no cover
            raise RuntimeError("缺少 anthropic 套件，無法使用 Anthropic provider")
        client = anthropic.AsyncAnthropic(api_key=key)
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text if response.content else ""

    base = settings.groq_api_base.rstrip("/")
    url = f"{base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    choices = data.get("choices", [])
    if not choices:
        return ""
    message = choices[0].get("message", {})
    return str(message.get("content", ""))
