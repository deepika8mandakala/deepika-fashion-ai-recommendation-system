# Technical Documentation

## AI Fashion Outfit Recommendation System

### Dare XAI – Machine Learning & AI Engineer Internship Assignment

---

# 1. Introduction

## Project Objective

The objective of this project is to develop an AI-powered Fashion Outfit Recommendation System capable of generating complete outfit recommendations using:

- User preferences
- Occasion context
- Fashion metadata
- Product images
- Outfit compatibility relationships

The system is designed as a retrieval-driven recommendation engine rather than a prompt-driven chatbot.

Unlike traditional LLM-based fashion assistants, recommendations are generated through retrieval, compatibility scoring, and ranking mechanisms while Large Language Models are limited to intent extraction and explanation generation.

---

# 2. Problem Statement

Users should be able to interact naturally with the system.

Example Queries:

- I need an outfit for a business meeting.
- Suggest something stylish for a beach vacation.
- I am attending a wedding next weekend.
- I am a 22-year-old male looking for summer clothes.

The system should recommend:

- Topwear
- Bottomwear
- Footwear
- Accessories

Along with:

- Compatibility Score
- Explanation
- Outfit Board
- Product Images

---

# 3. Dataset Analysis

## Dataset Source

Dare XAI Fashion Dataset

Repository:

https://github.com/DarexAI-AI-Startup/ML-TASK

---

## Dataset Components

### products.csv

Contains:

| Column | Description |
|----------|-------------|
| id | Unique Product Identifier |
| name | Product Name |
| brand | Product Brand |
| gender | Gender Category |
| category | Product Category |
| category_label | Human Readable Category |
| occasion | Intended Occasion |
| wear_type | Fashion Style |
| description | Product Description |
| image | Product Image Path |

---

### outfits.csv

Contains stylist-curated outfit combinations.

Example:

Formal Shirt
→ Formal Trouser
→ Blazer
→ Formal Shoes

Used as compatibility ground truth.

---

### Product Images

Collected from:

- Ajio
- Myntra
- Nykaa

Used for:

- Visual Retrieval
- Image Embeddings
- Outfit Board Generation

---

# 4. System Architecture

The system follows a layered architecture.

User
↓
Streamlit Frontend
↓
FastAPI Backend
↓
Intent Extraction Layer
↓
Recommendation Engine
↓
Hybrid Retrieval
↓
Compatibility Engine
↓
Ranking Engine
↓
Outfit Assembly
↓
Outfit Board Generator
↓
Explanation Generator
↓
Response

---

# 5. Intent Extraction Layer

## Purpose

Convert natural language user requests into structured recommendation parameters.

Example:

Input:

"I need a formal outfit for a business meeting."

Output:

{
  "occasion": "business",
  "style": "formal",
  "gender": "male"
}

---

## Implementation

Technology:

Gemini API

Responsibilities:

- Intent Detection
- Profile Extraction
- Explanation Generation

Non-Responsibilities:

- Product Retrieval
- Product Ranking
- Outfit Selection

These are handled by the recommendation engine.

---

# 6. Metadata Embedding Generation

## Objective

Represent product metadata as dense semantic vectors.

Input Features:

- Product Name
- Category
- Occasion
- Description
- Brand

Example Semantic Text:

Product: Arrow Formal Shirt

Category: Formal Shirt

Occasion: Office

Gender: Men

Description: White slim fit office shirt

---

## Model

Sentence Transformer

Model:

all-MiniLM-L6-v2

Embedding Dimension:

384

---

# 7. Image Embedding Generation

## Objective

Capture visual similarity between fashion products.

Features Learned:

- Color
- Texture
- Shape
- Pattern
- Visual Style

Models:

- FashionCLIP
- CLIP ViT-B/32

Output:

Image Feature Vector

---

# 8. Hybrid Embedding Layer

Metadata embeddings and image embeddings are combined.

Formula:

HybridEmbedding =
0.6 × ImageEmbedding
+
0.4 × MetadataEmbedding

Purpose:

- Semantic Understanding
- Visual Similarity
- Improved Retrieval Performance

---

# 9. Retrieval Engine

## Technology

FAISS

---

## Purpose

Retrieve relevant products from the fashion catalog.

Input:

User Query Embedding

Output:

Top-K Similar Products

---

## Why FAISS?

Compared with Chroma and Pinecone:

Advantages:

- Lightweight
- Fast
- Open Source
- No External Dependencies
- Suitable for Assignment Scale

---

# 10. Compatibility Engine

## Objective

Generate complete outfits using fashion relationships.

Data Source:

outfits.csv

---

## Compatibility Factors

- Occasion Matching
- Style Matching
- Category Relationships
- Fashion Rules

Example:

Formal Shirt
→ Formal Trouser
→ Blazer
→ Formal Shoes

Dress
→ Heels
→ Clutch

---

# 11. Ranking Engine

After retrieval and compatibility matching, products are ranked.

## Scoring Formula

FinalScore =
0.45 × Image Similarity
+
0.25 × Metadata Similarity
+
0.10 × Category Match
+
0.08 × Occasion Match
+
0.05 × Style Match
+
0.04 × Color Match
+
0.03 × Season Match

---

## Why Explicit Ranking?

Benefits:

- Explainable
- Auditable
- Easy to Tune
- Transparent

---

# 12. Outfit Assembly Engine

Constructs complete outfits.

Components:

- Topwear
- Bottomwear
- Footwear
- Accessories

Output Example:

Topwear:
Arrow Formal Shirt

Bottomwear:
Formal Trouser

Footwear:
Brown Derby Shoes

Accessory:
Leather Office Bag

---

# 13. Outfit Board Generator

## Objective

Create visual outfit recommendations.

Implementation:

Pillow (PIL)

---

## Workflow

1. Retrieve Product Images
2. Resize Images
3. Arrange Grid Layout
4. Save Outfit Board

Output:

Generated Outfit Board

No external image generation is used.

Only dataset product images are utilized.

---

# 14. Explanation Generator

Purpose:

Generate human-readable recommendation reasoning.

Example:

"The navy blazer complements the white formal shirt by creating a professional appearance suitable for business environments."

All explanations reference retrieved products.

---

# 15. API Design

Framework:

FastAPI

Endpoints:

| Endpoint | Method | Description |
|-----------|----------|-------------|
| /health | GET | Service Health Check |
| /chat | POST | Conversational Recommendations |
| /recommend | POST | Generate Outfit |
| /profile | POST | Store User Profile |
| /similar-item | POST | Similar Product Search |
| /metrics | GET | Service Metrics |

---

# 16. Frontend

Framework:

Streamlit

Features:

- Chat Interface
- User Profile Sidebar
- Outfit Display
- Product Images
- Outfit Boards
- Compatibility Scores

---

# 17. Testing Strategy

Framework:

Pytest

Covered Modules:

- API
- Recommendation Engine
- Compatibility Engine
- Data Processing

Result:

5 Tests Passed

---

# 18. Deployment

Docker Support Included

Files:

- Dockerfile
- docker-compose.yml

Deployment Command:

docker compose up --build

---

# 19. Engineering Decisions

## Why Retrieval Instead of Pure LLM?

Pure LLM Recommendation:

User Query
↓
LLM
↓
Recommendation

Issues:

- Hallucinations
- Inconsistent Results
- Difficult Evaluation

---

## Chosen Architecture

User Query
↓
Intent Extraction
↓
Retrieval
↓
Compatibility
↓
Ranking
↓
Recommendation

Benefits:

- Deterministic
- Explainable
- Scalable
- Production Friendly

---

# 20. Future Improvements

Potential Enhancements:

- FashionCLIP Fine-Tuning
- Graph Neural Networks
- Pairwise Ranking Models
- User Feedback Learning
- Online Learning
- Reinforcement Learning Personalization
- Large Scale Vector Databases

---

# 21. Conclusion

This project demonstrates the integration of:

- Recommendation Systems
- Information Retrieval
- Computer Vision
- Explainable AI
- FastAPI
- Streamlit

to create a production-oriented AI Fashion Assistant capable of generating complete, explainable, and visually grounded outfit recommendations using real products from the provided Dare XAI dataset.