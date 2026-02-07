from backend.config import settings
from .mock_provider import MockProvider
from .openai_provider import OpenAIProvider
from .base import AIProvider

def get_provider() -> AIProvider:
    if settings.ai_provider == "openai":
        return OpenAIProvider()
    return MockProvider()
