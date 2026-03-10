import logging

from app.config import settings

logger = logging.getLogger(__name__)

try:
    import anthropic
except ImportError:  # pragma: no cover
    anthropic = None


def _resolve_anthropic_key() -> str:
    anthropic_key = (settings.anthropic_api_key or "").strip()
    if not anthropic_key:
        raise RuntimeError("ANTHROPIC_API_KEY 未設定")
    return anthropic_key


def _pick_model(tier: str) -> str:
    normalized = tier.strip().lower()
    if normalized == "strong":
        return settings.anthropic_model_strong
    return settings.anthropic_model_fast


async def complete(
    *,
    system_prompt: str,
    user_prompt: str,
    tier: str = "fast",
    max_tokens: int = 4096,
) -> str:
    key = _resolve_anthropic_key()
    model = _pick_model(tier)

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
