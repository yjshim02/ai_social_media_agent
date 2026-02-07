import json
import os
import base64
from typing import Optional
from openai import OpenAI
from .base import AIProvider
from backend.config import settings

class OpenAIProvider(AIProvider):
    def __init__(self):
        self.client = OpenAI(timeout=settings.openai_timeout_s)

    def _extract_json(self, text: str) -> dict:
        # Try strict JSON parse first; then recover if model wrapped it.
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            # Find first and last braces
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                return json.loads(text[start:end+1])
            raise

    def generate_json(self, prompt: str) -> dict:
        # Use Responses API (recommended for new projects)
        resp = self.client.responses.create(
            model=settings.openai_text_model,
            input=prompt,
        )
        return self._extract_json(resp.output_text)

    def generate_image_b64(self, prompt: str, size: str = "1024x1024") -> Optional[str]:
        # Use Images API for a single-shot generation (returns base64)
        result = self.client.images.generate(
            model=settings.openai_image_model,
            prompt=prompt,
            size=size
        )
        return result.data[0].b64_json
