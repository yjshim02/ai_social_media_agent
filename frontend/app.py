import base64
import json
import requests
import streamlit as st
from PIL import Image
from io import BytesIO

API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Social Media Agent", layout="wide")
st.title("AI Social Media Agent")
st.caption("Generate on-brand Hack-Nation posts with an agentic self-feedback loop + human-in-the-loop refinement.")

with st.sidebar:
    st.header("Inputs")
    intent = st.text_area("Post intent", value="Announce Hack-Nation during Super Bowl season and invite teams to apply.", height=120)
    event = st.selectbox("Event reference", ["Super Bowl", "Olympics"])
    platform = st.selectbox("Platform", ["LinkedIn", "Instagram"])
    generate_btn = st.button("Generate Posts 🚀", type="primary")

def render_image(b64_str: str):
    # mock provider returns base64-encoded SVG text; OpenAI returns base64 PNG.
    # We try PNG decode first; if it fails, render SVG via markdown.
    try:
        img_bytes = base64.b64decode(b64_str)
        img = Image.open(BytesIO(img_bytes))
        st.image(img, use_container_width=True)
    except Exception:
        svg_text = base64.b64decode(b64_str).decode("utf-8", errors="ignore")
        st.markdown(svg_text, unsafe_allow_html=True)

def score_badges(critiques):
    if not critiques:
        return
    last = critiques[-1]
    st.write(
        f"**Scores** — brand {last['brand_consistency']}/5 · clarity {last['clarity']}/5 · CTA {last['cta_strength']}/5 · readability {last['image_text_readability']}/5 · postable: **{last['postability']}**"
    )
    st.caption(f"Latest improvement: {last['improvements']}")


def judge_badge(judge: dict | None):
    if not judge:
        return
    st.write(
        f"**Judge** — overall {judge['overall_score']}/100 · brand {judge['brand_fit']}/100 · clarity {judge['clarity']}/100 · CTA {judge['cta_effectiveness']}/100 · visual {judge['visual_readability']}/100"
    )
    st.caption(judge.get("rationale", ""))

if "variants" not in st.session_state:
    st.session_state.variants = None
if "brand_profile" not in st.session_state:
    st.session_state.brand_profile = None
if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = None
if "refined" not in st.session_state:
    st.session_state.refined = None

if generate_btn:
    with st.spinner("Generating… (3 variants + 2 internal critique loops each)"):
        r = requests.post(f"{API_URL}/generate", json={"intent": intent, "event": event, "platform": platform}, timeout=300)
        r.raise_for_status()
        data = r.json()
        st.session_state.brand_profile = data["brand_profile"]
        st.session_state.variants = data["variants"]
        st.session_state.selected_idx = None
        st.session_state.refined = None

if st.session_state.brand_profile:
    st.subheader("Inferred Brand Profile (machine-readable)")
    st.json(st.session_state.brand_profile)

if st.session_state.variants:
    st.subheader("Generated Variants")
    cols = st.columns(3)
    for i, v in enumerate(st.session_state.variants):
        with cols[i]:
            title = f"Variant {i+1}"
            if i == 0 and v.get("judge"):
                title += "  🏅 (Top scored)"
            st.markdown(f"### {title}")
            if v.get("background_image_b64"):
                render_image(v["background_image_b64"])
            st.markdown("**Text overlay**")
            st.code(v["text_overlay"])
            st.markdown("**Caption**")
            st.write(v["caption"])
            judge_badge(v.get("judge"))
            score_badges(v.get("critiques", []))
            if st.button(f"Select Variant {i+1}", key=f"select_{i}"):
                st.session_state.selected_idx = i
                st.session_state.refined = None

if st.session_state.selected_idx is not None:
    st.divider()
    st.subheader("Human-in-the-loop refinement")
    selected = st.session_state.variants[st.session_state.selected_idx]
    feedback = st.text_input("Your feedback (tone/CTA/layout/etc.)", value="Make it punchier and add a clearer CTA.")
    if st.button("Refine Selected Variant ✨", type="primary"):
        payload = dict(selected)
        payload["event"] = event
        with st.spinner("Refining…"):
            r = requests.post(f"{API_URL}/refine", json={"selected_post": payload, "feedback": feedback}, timeout=300)
            r.raise_for_status()
            st.session_state.refined = r.json()

if st.session_state.refined:
    st.subheader("Refined Output")
    v = st.session_state.refined["variant"]
    if v.get("background_image_b64"):
        render_image(v["background_image_b64"])
    st.markdown("**Text overlay**")
    st.code(v["text_overlay"])
    st.markdown("**Caption**")
    st.write(v["caption"])
    judge_badge(v.get("judge"))
    critiques = v.get("critiques", [])
    if critiques:
        st.markdown("**Critique log**")
        st.json(critiques)
