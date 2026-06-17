"""Shared helpers for agents."""


def extract_usage(resp) -> dict:
    """Best-effort extraction of token usage across different LLM response objects."""
    usage = getattr(resp, "usage_metadata", None)
    if usage:
        return {
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "total_tokens": usage.get("total_tokens"),
        }

    meta = getattr(resp, "response_metadata", {}) or {}
    token_usage = meta.get("token_usage") or meta.get("usage")
    if token_usage:
        return {
            "input_tokens": token_usage.get("prompt_tokens") or token_usage.get("input_tokens"),
            "output_tokens": token_usage.get("completion_tokens") or token_usage.get("output_tokens"),
            "total_tokens": token_usage.get("total_tokens"),
        }

    return {"input_tokens": None, "output_tokens": None, "total_tokens": None}