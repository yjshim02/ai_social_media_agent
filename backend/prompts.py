def brand_inference_prompt(event: str) -> str:
    return f"""You are a brand strategist + social media designer.

We are building posts for Hack-Nation (a global AI hackathon). Only use the given event context: {event}.
Infer a practical, approximate brand profile that can be used as JSON constraints for downstream agents.

Return STRICT JSON with keys:
- brand_voice: {{tone, emoji_usage, cta_style}}
- visual_identity: {{colors, style, imagery}}
- language_rules: {{sentence_length, avoid, must_include}}

Rules:
- Be concise and actionable, not poetic.
- Keep colors to 2–4 entries.
- Keep avoid/must_include to <= 6 items each.
"""


def post_generation_prompt(intent: str, platform: str, event: str, brand_profile_json: str, variant_id: int) -> str:
    return f"""You are a junior social media manager + designer working at machine speed.

TASK: Create ONE on-brand post variant for Hack-Nation.

Context:
- Event reference: {event} (use subtle sports metaphors, avoid trademarked team names/logos)
- Platform: {platform}
- Intent: {intent}

Brand constraints (JSON):
{brand_profile_json}

Output STRICT JSON with keys:
- caption: string
- text_overlay: string (max 8 words, no emojis)
- image_prompt: string (abstract sports energy; no faces; no logos; leave space for centered overlay)

Platform norms:
- LinkedIn: 2–3 short paragraphs max, professional but energetic, CTA at end.
- Instagram: shorter, punchier, line breaks ok, 3–8 hashtags at end, CTA.

Variant behavior:
- Make this distinct from other variants (variation #{variant_id}).
"""


def critique_prompt(platform: str, event: str, brand_profile_json: str, post_json: str) -> str:
    return f"""You are a strict social media QA reviewer.

Evaluate the post against explicit criteria and suggest ONE concrete improvement.

Context:
- Platform: {platform}
- Event: {event}

Brand constraints (JSON):
{brand_profile_json}

Post (JSON):
{post_json}

Return STRICT JSON with keys:
- brand_consistency: integer 1-5
- clarity: integer 1-5
- cta_strength: integer 1-5
- image_text_readability: integer 1-5
- postability: "yes" or "no"
- improvements: string (one actionable improvement; be specific)
"""


def revise_prompt(event: str, platform: str, brand_profile_json: str, post_json: str, critique_json: str, human_feedback: str | None) -> str:
    feedback_block = f"\nHuman feedback: {human_feedback}\n" if human_feedback else ""
    return f"""You are revising a social media post to improve quality while staying on-brand.

Event: {event}
Platform: {platform}

Brand constraints (JSON):
{brand_profile_json}

Current post (JSON):
{post_json}

Latest critique (JSON):
{critique_json}
{feedback_block}

Return STRICT JSON with keys:
- caption: string
- text_overlay: string (max 8 words, no emojis)
- image_prompt: string
"""


def judge_prompt(platform: str, event: str, brand_profile_json: str, post_json: str) -> str:
    return f"""You are a senior social media lead reviewing if this is safe to post.

Score the post using EXPLICIT criteria (0-100). Be harsh but fair.

Context:
- Platform: {platform}
- Event: {event}

Brand constraints (JSON):
{brand_profile_json}

Post (JSON):
{post_json}

Scoring rubric:
- brand_fit: matches tone/CTA/language rules (0-100)
- clarity: message is instantly understandable (0-100)
- cta_effectiveness: strong, specific CTA for the platform (0-100)
- visual_readability: overlay is short + image prompt leaves space, mobile-friendly (0-100)

overall_score must be a weighted average: 35% brand_fit, 30% clarity, 20% cta_effectiveness, 15% visual_readability.

Return STRICT JSON with keys:
- overall_score: int 0-100
- brand_fit: int 0-100
- clarity: int 0-100
- cta_effectiveness: int 0-100
- visual_readability: int 0-100
- rationale: string (2-4 sentences, concrete)
"""


 