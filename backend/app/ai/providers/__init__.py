import os
from .base_provider import BaseAIProvider
from .mock_provider import MockAIProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider

def get_ai_provider(provider_type: str = "auto") -> BaseAIProvider:
    provider_type = provider_type.lower()
    if provider_type == "gemini":
        return GeminiProvider()
    elif provider_type == "openai":
        return OpenAIProvider()
    elif provider_type == "mock":
        return MockAIProvider()

    # Auto mode: select based on configured non-placeholder keys
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    if gemini_key and not gemini_key.startswith("your_"):
        return GeminiProvider()
    if openai_key and not openai_key.startswith("your_") and len(openai_key) > 20:
        return OpenAIProvider()

    return MockAIProvider()

__all__ = ["BaseAIProvider", "MockAIProvider", "OpenAIProvider", "GeminiProvider", "get_ai_provider"]
