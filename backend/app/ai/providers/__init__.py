import os
from .base_provider import BaseAIProvider
from .mock_provider import MockAIProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from .openrouter_provider import OpenRouterProvider

def get_ai_provider(provider_type: str = "auto") -> BaseAIProvider:
    provider_type = provider_type.lower()
    if provider_type == "openrouter":
        return OpenRouterProvider()
    elif provider_type == "gemini":
        return GeminiProvider()
    elif provider_type == "openai":
        return OpenAIProvider()
    elif provider_type == "mock":
        return MockAIProvider()

    # Auto mode: OpenRouter → OpenAI → Gemini → Mock
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    # OpenRouter keys start with 'sk-or-'
    if openrouter_key and openrouter_key.startswith("sk-or-") and len(openrouter_key) > 20:
        return OpenRouterProvider()

    # OpenAI keys start with 'sk-' (not 'sk-or-')
    if openai_key and openai_key.startswith("sk-") and not openai_key.startswith("sk-or-") and len(openai_key) > 30:
        return OpenAIProvider()

    # Gemini keys start with 'AIza'
    if gemini_key and gemini_key.startswith("AIza") and len(gemini_key) > 20:
        return GeminiProvider()

    return MockAIProvider()

__all__ = [
    "BaseAIProvider", "MockAIProvider", "OpenAIProvider",
    "GeminiProvider", "OpenRouterProvider", "get_ai_provider"
]
