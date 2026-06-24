"""Streamlit interface for Fashion AI."""

from __future__ import annotations

import os
from pathlib import Path

import requests
import streamlit as st
from requests import RequestException


API_URL = os.getenv("FASHION_AI_API_URL", "http://127.0.0.1:8000")


def safe_image(path: str | None, caption: str | None = None) -> None:
    """Render local files or remote URLs."""

    if not path:
        return

    try:
        if path.startswith("http://") or path.startswith("https://"):
            st.image(path, caption=caption, use_container_width=True)
            return

        image_path = Path(path)

        if image_path.exists():
            st.image(
                str(image_path),
                caption=caption,
                use_container_width=True,
            )
        else:
            st.warning(f"Image file missing: {path}")

    except Exception as exc:
        st.warning(f"Could not render image: {exc}")

st.set_page_config(page_title="Fashion AI", page_icon="shirt", layout="wide")
st.title("Fashion AI Outfit Recommender")
st.image(
    "https://deepika-fashion-ai-recommendation-system-mvcz.onrender.com/images/myntra/28569210.jpg",
    caption="Test Image",
    use_container_width=True,
)
st.caption(f"API: {API_URL}")

with st.sidebar:
    st.header("Profile")
    gender = st.selectbox("Gender", ["", "male", "female", "unisex"])
    age = st.number_input("Age", min_value=1, max_value=100, value=22)
    occasion = st.selectbox("Occasion", ["", "casual", "office", "party", "festive", "wedding", "winter", "sports", "vacation"])
    season = st.selectbox("Season", ["", "summer", "winter", "spring", "autumn", "all season"])
    style = st.selectbox("Preferred style", ["", "formal", "smart casual", "casual", "ethnic", "streetwear", "beach"])
    colors = st.multiselect("Preferred colors", ["white", "black", "navy", "blue", "grey", "brown", "beige", "red"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "shown_product_ids" not in st.session_state:
    st.session_state.shown_product_ids = []

button_cols = st.columns(2)
generate_clicked = button_cols[0].button("Generate outfit", use_container_width=True)
regenerate_clicked = button_cols[1].button("Regenerate", use_container_width=True)
query = st.chat_input("Ask for an outfit...")

for role, content in st.session_state.messages:
    with st.chat_message(role):
        st.write(content)

prompt = query
exclude_product_ids: list[str] = []
if generate_clicked and not prompt:
    prompt = "Generate outfit according to my profile"
if regenerate_clicked:
    prompt = "Regenerate a different outfit according to my profile"
    exclude_product_ids = st.session_state.shown_product_ids

if prompt:
    st.session_state.messages.append(("user", prompt))
    with st.chat_message("user"):
        st.write(prompt)

    profile = {
        "occasion": occasion or "casual",
        "gender": gender or None,
        "age": age,
        "season": season or None,
        "preferred_style": style or None,
        "preferred_colors": colors,
        "exclude_product_ids": exclude_product_ids,
    }

    try:
        with st.spinner("Retrieving, ranking, and assembling outfits..."):
            response = requests.post(
                f"{API_URL}/chat",
                json={"message": prompt, "profile": profile},
                timeout=90,
            )
    except RequestException as exc:
        st.error(
            "The API did not respond. Start it from the project root with "
            "`uvicorn app.api.main:app --host 127.0.0.1 --port 8000`."
        )
        st.info("For the fast local demo, keep `USE_TRANSFORMER_EMBEDDINGS=false`.")
        st.exception(exc)
        st.stop()

    if response.ok:
        payload = response.json()
        st.session_state.messages.append(("assistant", f"Found {len(payload['outfits'])} ranked outfits."))
        if not payload["outfits"]:
            st.warning("No valid-image outfit matched this profile. Try a broader occasion or clear regenerate exclusions.")
            st.stop()
        shown_ids = []
        for outfit in payload["outfits"]:
            st.subheader(f"Compatibility Score: {outfit['compatibility_score']}/100")
            if outfit.get("generated_image_path"):
                safe_image(outfit["generated_image_path"], "Generated outfit board from dataset images")
            for reason in outfit["reasoning"]:
                st.write(reason)
            cols = st.columns(4)
            for index, slot in enumerate(["topwear", "bottomwear", "footwear"]):
                item = outfit.get(slot)
                with cols[index]:
                    st.caption(slot.upper())
                    if item:
                        if item.get("image_path"):
                            safe_image(item["image_path"])
                        st.metric(item["name"], f"{item['score']}/100")
                        shown_ids.append(item["id"])
                        st.write(f"{item['color']} {item['article_type']} | {item['usage']} | {item['season']}")
                        st.progress(min(item["score"] / 100, 1.0))
            with cols[3]:
                st.caption("ACCESSORY")
                for item in outfit.get("accessories", []):
                    if item.get("image_path"):
                        safe_image(item["image_path"])
                    st.metric(item["name"], f"{item['score']}/100")
                    shown_ids.append(item["id"])
            with st.expander("Score breakdown"):
                st.json(outfit)
        st.session_state.shown_product_ids = list(dict.fromkeys(shown_ids))
    else:
        st.error(response.text)
