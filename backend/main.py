from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import GenerateRequest, RefineRequest, PostVariant
from backend.agents import (
    infer_brand,
    generate_variants,
    agentic_self_feedback_loop,
    attach_background_image,
    critique_post,
    revise_post,
    score_variants,
    judge_post,
)

app = FastAPI(title="AI Social Media Agent")

# Allow local Streamlit to call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/generate")
def generate(req: GenerateRequest):
    brand = infer_brand(req.event)
    variants = generate_variants(req.intent, req.platform, req.event, brand, n_variants=3)

    improved = []
    for v in variants:
        v2 = agentic_self_feedback_loop(req.event, req.platform, brand, v, n_iters=2)
        v2 = attach_background_image(v2)
        improved.append(v2.model_dump())

    # Judge pass: score and rank variants (fresh rubric, separate call)
    hydrated = [PostVariant(**v) for v in improved]
    scored = score_variants(req.event, req.platform, brand, hydrated)
    scored_sorted = sorted(scored, key=lambda x: (x.judge.overall_score if x.judge else 0), reverse=True)

    return {
        "brand_profile": brand.model_dump(),
        "variants": [v.model_dump() for v in scored_sorted],
    }

@app.post("/refine")
def refine(req: RefineRequest):
    # Re-infer brand from event if the client included it in the selected_post
    post_obj = req.selected_post
    event = post_obj.get("event", "Super Bowl")
    platform = post_obj.get("platform", "LinkedIn")

    brand = infer_brand(event)

    # Build PostVariant from dict
    v = PostVariant(
        platform=platform,
        caption=post_obj["caption"],
        text_overlay=post_obj["text_overlay"],
        image_prompt=post_obj["image_prompt"],
        background_image_b64=post_obj.get("background_image_b64"),
        critiques=[],
    )

    # Human-in-the-loop: critique once, then revise using human feedback
    c = critique_post(platform, event, brand, v)
    v.critiques.append(c)
    v = revise_post(event, platform, brand, v, c, human_feedback=req.feedback)
    v = attach_background_image(v)

    # Re-score refined variant for convenience
    v.judge = judge_post(platform, event, brand, v)

    out = v.model_dump()
    out["event"] = event
    return {"brand_profile": brand.model_dump(), "variant": out}
