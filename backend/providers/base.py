from abc import ABC, abstractmethod
from typing import Optional

class AIProvider(ABC):
    @abstractmethod
    def generate_json(self, prompt: str) -> dict:
        ...

    @abstractmethod
    def generate_image_b64(self, prompt: str, size: str = "1024x1024") -> Optional[str]:
        ...
