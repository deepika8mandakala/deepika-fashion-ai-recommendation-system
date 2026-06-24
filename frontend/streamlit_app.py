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
        # Remote URL
        if path.startswith("http://") or path.startswith("https://"):
            st.image(path, caption=caption, use_container_width=True)
            return

        # Local file
        image_path = Path(path)

        if image_path.exists():
            st.image(
                str(image_path),
                caption=caption,
                use_container_width=True,
            )
        else:
            st.warning(f"Image file missing: {image_path.name}")

    except Exception as exc:
        st.warning(f"Could not render image: {exc}")
