import json
from typing import Any, Dict, List, Optional
from backend.schemas import BrandProfile, PostVariant, Critique, JudgeResult
from backend.prompts import (
    brand_inference_prompt,
    post_generation_prompt,
    critique_prompt,
    revise_prompt,
    judge_prompt,
)
from backend.providers.factory import get_provider

provider = get_provider()

def infer_brand(event: str) -> BrandProfile:
    data = provider.generate_json(brand_inference_prompt(event))
    return BrandProfile(**data)

def generate_variants(intent: str, platform: str, event: str, brand: BrandProfile, n_variants: int = 3) -> List[PostVariant]:
    brand_json = brand.model_dump_json(indent=2)
    variants: List[PostVariant] = []
    for k in range(1, n_variants + 1):
        data = provider.generate_json(post_generation_prompt(intent, platform, event, brand_json, k))
        variant = PostVariant(
            platform=platform,
            caption=data["caption"].strip(),
            text_overlay=data["text_overlay"].strip(),
            image_prompt=data["image_prompt"].strip(),
        )
        variants.append(variant)
    return variants

def critique_post(platform: str, event: str, brand: BrandProfile, post: PostVariant) -> Critique:
    brand_json = brand.model_dump_json(indent=2)
    post_json = json.dumps(
        {"caption": post.caption, "text_overlay": post.text_overlay, "image_prompt": post.image_prompt},
        ensure_ascii=False,
        indent=2,
    )
    data = provider.generate_json(critique_prompt(platform, event, brand_json, post_json))
    return Critique(**data)


def judge_post(platform: str, event: str, brand: BrandProfile, post: PostVariant) -> JudgeResult:
    """Independent scoring pass used to rank variants.

    This is intentionally a separate model call from the critique loop so that
    we can compare multiple variants with a consistent rubric.
    """
    brand_json = brand.model_dump_json(indent=2)
    post_json = json.dumps(
        {"caption": post.caption, "text_overlay": post.text_overlay, "image_prompt": post.image_prompt},
        ensure_ascii=False,
        indent=2,
    )
    data = provider.generate_json(judge_prompt(platform, event, brand_json, post_json))
    return JudgeResult(**data)


def revise_post(event: str, platform: str, brand: BrandProfile, post: PostVariant, critique: Critique, human_feedback: Optional[str] = None) -> PostVariant:
    brand_json = brand.model_dump_json(indent=2)
    post_json = json.dumps(
        {"caption": post.caption, "text_overlay": post.text_overlay, "image_prompt": post.image_prompt},
        ensure_ascii=False,
        indent=2,
    )
    critique_json = critique.model_dump_json(indent=2)
    data = provider.generate_json(revise_prompt(event, platform, brand_json, post_json, critique_json, human_feedback))
    post.caption = data["caption"].strip()
    post.text_overlay = data["text_overlay"].strip()
    post.image_prompt = data["image_prompt"].strip()
    return post

def attach_background_image(post: PostVariant) -> PostVariant:
    # Generate a background image (or mock placeholder) and attach base64 string
    b64 = provider.generate_image_b64(post.image_prompt)
    post.background_image_b64 = b64
    return post

def agentic_self_feedback_loop(event: str, platform: str, brand: BrandProfile, post: PostVariant, n_iters: int = 2) -> PostVariant:
    for _ in range(n_iters):
        c = critique_post(platform, event, brand, post)
        post.critiques.append(c)
        post = revise_post(event, platform, brand, post, c)
    return post


def score_variants(event: str, platform: str, brand: BrandProfile, variants: List[PostVariant]) -> List[PostVariant]:
    """Attach judge scores to each variant."""
    for v in variants:
        v.judge = judge_post(platform, event, brand, v)
    return variants
