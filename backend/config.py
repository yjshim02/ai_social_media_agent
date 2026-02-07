import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    ai_provider: str = os.getenv("AI_PROVIDER", "mock").lower()  # "mock" or "openai"
    openai_text_model: str = os.getenv("OPENAI_TEXT_MODEL", "gpt-5.2")
    openai_image_model: str = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
    openai_timeout_s: int = int(os.getenv("OPENAI_TIMEOUT_S", "60"))

settings = Settings()
