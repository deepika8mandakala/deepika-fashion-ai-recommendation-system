# Continue This Project From Another Account

## Project Location

```powershell
cd C:\Users\manda\Documents\Codex\2026-06-23\files-mentioned-by-the-user-role\outputs\fashion-ai
```

## Current Status

- FastAPI backend exists and was verified.
- Streamlit frontend exists.
- Root endpoint `/` was added so the base API URL no longer returns `{"detail":"Not Found"}`.
- `/health` works.
- `/chat` works.
- Tests passed: `4 passed`.
- Fast local embeddings are enabled by default with `USE_TRANSFORMER_EMBEDDINGS=false`.

## Verified Run Commands

API:

```powershell
set USE_TRANSFORMER_EMBEDDINGS=false
python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Streamlit:

```powershell
set FASHION_AI_API_URL=http://127.0.0.1:8000
python -m streamlit run frontend/streamlit_app.py
```

Open:

- API docs: http://127.0.0.1:8000/docs
- Streamlit: http://localhost:8501
- Health: http://127.0.0.1:8000/health

## Dataset To Use Next

GitHub repo:

```text
https://github.com/DarexAI-AI-Startup/ML-TASK.git
```

The repo contains:

- `products.csv`
- `outfits.csv`
- `curated25.xlsx`
- `images/`

Important requirement from user:

> Use this dataset only. Recommendations should show/generate suitable outfit images from the given dataset, not hallucinated external products.

## Next Implementation Goal

Integrate the GitHub dataset into the existing app:

1. Clone/download `DarexAI-AI-Startup/ML-TASK`.
2. Copy or reference its files under `data/darex/`.
3. Add a loader that maps `products.csv` columns to the internal `Product` model:
   - `id` -> `id`
   - `name` -> `product_display_name`
   - `gender` -> `gender`
   - `category_label` or `category` -> `article_type`
   - `occasion` -> `usage`
   - `wear_type` -> style metadata
   - `description` + `tags` -> semantic description
   - `image` -> image path rooted at the dataset directory
4. Add outfit-ground-truth loading from `outfits.csv`.
5. Modify recommendation response to include image paths for selected dataset items.
6. Modify Streamlit outfit cards to display actual dataset images.
7. Add an outfit image composer:
   - Load selected product images with Pillow.
   - Resize to common tile size.
   - Compose topwear/bottomwear/footwear/accessory into one generated outfit board.
   - Save generated boards under `cache/generated_outfits/`.
   - Return the generated board path in API response.
8. Ensure no external image generation is used. Use only product images from the dataset.

## Suggested Prompt For Next Account

```text
We are continuing a Codex project at:
C:\Users\manda\Documents\Codex\2026-06-23\files-mentioned-by-the-user-role\outputs\fashion-ai

Read NEXT_ACCOUNT_HANDOFF.md first.

Task: integrate the dataset from https://github.com/DarexAI-AI-Startup/ML-TASK.git into the existing Fashion AI app. Use that dataset only. Recommendations must display actual product images from the dataset and generate a composed outfit board image from selected dataset product images. Do not use external/hallucinated product images.

Keep USE_TRANSFORMER_EMBEDDINGS=false by default for fast local runs. Preserve FastAPI + Streamlit. Verify /health, /chat, Streamlit image rendering, and tests.
```

