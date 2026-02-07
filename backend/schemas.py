from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any

EventType = Literal["Super Bowl", "Olympics"]
PlatformType = Literal["LinkedIn", "Instagram"]

class GenerateRequest(BaseModel):
    intent: str = Field(..., description="What the user wants to post")
    event: EventType
    platform: PlatformType
    constraints: Optional[Dict[str, Any]] = Field(default=None, description="Optional: date, tone, CTA, etc.")
    rag_payload: Optional[Dict[str, Any]] = Field(default=None, description="Optional: speaker names, prizes, etc.")

class RefineRequest(BaseModel):
    selected_post: Dict[str, Any] = Field(..., description="The chosen post object to refine")
    feedback: str = Field(..., description="User feedback for edits")

class BrandProfile(BaseModel):
    brand_voice: Dict[str, Any]
    visual_identity: Dict[str, Any]
    language_rules: Dict[str, Any]

class Critique(BaseModel):
    brand_consistency: int = Field(..., ge=1, le=5)
    clarity: int = Field(..., ge=1, le=5)
    cta_strength: int = Field(..., ge=1, le=5)
    image_text_readability: int = Field(..., ge=1, le=5)
    postability: Literal["yes", "no"]
    improvements: str


class JudgeResult(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    brand_fit: int = Field(..., ge=0, le=100)
    clarity: int = Field(..., ge=0, le=100)
    cta_effectiveness: int = Field(..., ge=0, le=100)
    visual_readability: int = Field(..., ge=0, le=100)
    rationale: str

class PostVariant(BaseModel):
    platform: PlatformType
    caption: str
    text_overlay: str
    image_prompt: str
    background_image_b64: Optional[str] = None  # base64-encoded PNG (OpenAI) or SVG (mock)
    critiques: List[Critique] = Field(default_factory=list)
    judge: Optional[JudgeResult] = None
