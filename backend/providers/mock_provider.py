import base64
import json
from typing import Optional
from .base import AIProvider

def _svg_placeholder(title: str) -> str:
    # Simple deterministic SVG that always renders (good for demos)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024">
      <rect width="100%" height="100%" fill="#111111"/>
      <rect x="80" y="80" width="864" height="864" fill="#F5C518" opacity="0.12"/>
      <text x="50%" y="45%" dominant-baseline="middle" text-anchor="middle"
            font-family="Arial" font-size="52" fill="#FFFFFF">MOCK IMAGE</text>
      <text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle"
            font-family="Arial" font-size="32" fill="#FFFFFF" opacity="0.9">{title}</text>
    </svg>'''
    return svg

class MockProvider(AIProvider):
    def generate_json(self, prompt: str) -> dict:
        # Very simple heuristics to keep the pipeline running without API credits.
        p = prompt.lower()
        if "infer a practical" in p:
            return {
                "brand_voice": {"tone": "energetic, optimistic, builder-focused", "emoji_usage": "light", "cta_style": "direct, action-oriented"},
                "visual_identity": {"colors": ["black", "gold"], "style": "bold typography, high contrast", "imagery": "abstract sports energy"},
                "language_rules": {"sentence_length": "short", "avoid": ["corporate jargon", "long paragraphs"], "must_include": ["Hack-Nation", "AI", "call to action"]}
            }
        if "qa reviewer" in p:
            return {
                "brand_consistency": 4,
                "clarity": 4,
                "cta_strength": 3,
                "image_text_readability": 4,
                "postability": "yes",
                "improvements": "Make the CTA more specific (e.g., add a deadline or link instruction)."
            }
        if "overall_score" in p and "weighted average" in p:
            return {
                "overall_score": 84,
                "brand_fit": 86,
                "clarity": 82,
                "cta_effectiveness": 78,
                "visual_readability": 90,
                "rationale": "On-brand and clear, but the CTA could be more specific (deadline/link). Overlay length looks safe for mobile."
            }
        # post generation / revision
        return {
            "caption": """🏈 Hack-Nation is on. Build something that wins.

Bring your best idea, ship a demo, and join builders worldwide.

👉 Apply now + invite a friend.""",
            "text_overlay": "Game On: Hack-Nation",
            "image_prompt": "Abstract sports-inspired energy background, black and gold, high contrast, space for centered text overlay, no logos, no faces."
        }

    def generate_image_b64(self, prompt: str, size: str = "1024x1024") -> Optional[str]:
        svg = _svg_placeholder("Hack-Nation")
        return base64.b64encode(svg.encode("utf-8")).decode("utf-8")
