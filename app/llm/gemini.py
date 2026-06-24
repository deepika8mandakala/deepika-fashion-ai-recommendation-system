"""Gemini intent parser with strict non-recommender responsibility."""

from __future__ import annotations

import json
import re

from app.config.settings import get_settings
from app.schemas.recommendation import UserIntent


OCCASION_KEYWORDS = {
    "business meeting": "business",
    "office": "office",
    "interview": "interview",
    "wedding": "wedding",
    "festive": "festive",
    "ethnic": "festive",
    "farewell": "party",
    "college": "casual",
    "beach": "beach",
    "vacation": "vacation",
    "gym": "sports",
    "sports": "sports",
    "party": "party",
    "winter": "winter",
}

STYLE_KEYWORDS = {
    "smart casual": "smart casual",
    "formal": "formal",
    "ethnic": "ethnic",
    "streetwear": "streetwear",
    "casual": "casual",
}

COLOR_WORDS = {
    "white",
    "black",
    "navy",
    "blue",
    "grey",
    "gray",
    "brown",
    "beige",
    "red",
    "green",
    "olive",
    "pink",
}


class GeminiIntentParser:
    """Extract structured intent; never selects products."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def parse(self, query: str, profile: UserIntent | None = None) -> UserIntent:
        """Use Gemini when configured, otherwise deterministic keyword extraction."""

        if self.settings.gemini_api_key:
            try:
                return self._parse_with_gemini(query, profile)
            except Exception:
                pass
        return self._parse_locally(query, profile)

    def _parse_with_gemini(self, query: str, profile: UserIntent | None) -> UserIntent:
        import google.generativeai as genai

        genai.configure(api_key=self.settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            "Extract only structured fashion intent as JSON with keys occasion, gender, age, "
            "preferred_colors, preferred_style, season, query. Do not recommend products.\n"
            f"Query: {query}"
        )
        response = model.generate_content(prompt)
        payload = json.loads(response.text.strip().strip("`json").strip("`"))
        base = profile.model_dump() if profile else {}
        base.update({key: value for key, value in payload.items() if value not in (None, "", [])})
        return UserIntent(**base, query=query)

    def _parse_locally(self, query: str, profile: UserIntent | None) -> UserIntent:
        text = query.lower()
        base = profile.model_dump() if profile else {}
        occasion = base.get("occasion") or "casual"
        for keyword, value in OCCASION_KEYWORDS.items():
            if keyword in text:
                occasion = value
                break
        style = base.get("preferred_style")
        for keyword, value in STYLE_KEYWORDS.items():
            if keyword in text:
                style = value
                break
        if style == "ethnic" and (not occasion or occasion == "casual"):
            occasion = "festive"
        gender = base.get("gender")
        if " male" in f" {text}" or "for men" in text:
            gender = "male"
        elif " female" in f" {text}" or "for women" in text:
            gender = "female"
        age_match = re.search(r"\b(\d{2})[- ]?year", text)
        colors = list(dict.fromkeys(base.get("preferred_colors", []) + [word for word in COLOR_WORDS if word in text]))
        season = base.get("season")
        for candidate in ("summer", "winter", "spring", "autumn", "fall"):
            if candidate in text:
                season = "autumn" if candidate == "fall" else candidate
        return UserIntent(
            occasion=occasion,
            gender=gender,
            age=int(age_match.group(1)) if age_match else base.get("age"),
            preferred_colors=colors,
            preferred_style=style,
            season=season,
            query=query,
            exclude_product_ids=base.get("exclude_product_ids", []),
        )
