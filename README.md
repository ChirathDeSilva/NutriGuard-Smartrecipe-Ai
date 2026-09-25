# NutriGuard - SmartRecipe AI

SmartRecipe AI (NutriGuard) is a secure, agentic multi-agent recipe recommendation, nutrition, and food safety system. It solves the problem of finding personalized recipes based on available household ingredients while strictly enforcing health, allergen, dietary, and preparation time constraints.

---

## 🌟 Key Features

1. **5-Agent AI Pipeline**:
   - **Agent 1: Query Agent** (spaCy NLP entity extraction & constraint parsing).
   - **Agent 2: Retrieval Agent** (BM25 local search + TheMealDB external API fallback).
   - **Agent 3: Safety Agent** (100% deterministic Python set logic for allergen & dietary blocking — ZERO LLM).
   - **Agent 4: Ranking Agent** (Linear weighted multi-factor scoring formula).
   - **Agent 5: Response Agent** (Grounded Google Gemini LLM explanation & formatting).

2. **📰 Recipe Nutrition Tips & Food Safety News**:
   - Curated feed of evidence-based dietary recommendations, macronutrient balance tips, and allergen warnings.
   - Categorized by Nutrition Tips and Health News with instant search and filtering.
   - Dedicated REST API (`GET /api/tips`) and multi-page Streamlit view.

3. **Interactive Frontend**:
   - Multi-turn recipe chat interface with customizable allergy and dietary filters.
   - Plotly horizontal macronutrient charts (Calories, Protein, Carbs, Fats).
   - Responsive recipe & article cards.

---

## 🏗️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLite, SQLAlchemy 2.0, Pydantic v2
- **NLP & Search**: spaCy (`en_core_web_sm`), Rank-BM25
- **AI / LLM**: Google Gemini API (`gemini-1.5-flash` / `google-genai`)
- **Frontend**: Streamlit, Plotly, Requests
- **Testing**: Pytest

---

## 🚀 Quickstart Guide

### 1. Activate Environment & Install Dependencies
```powershell
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure Environment (`.env`)
Make sure your `.env` contains your API credentials:
```env
GEMINI_API_KEY=your_gemini_api_key_here
USDA_API_KEY=your_usda_api_key_here
THEMEALDB_API_KEY=1
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///./backend/data/recipes.db
```

### 3. Seed Database
```powershell
python -m backend.app.seed_db
```

### 4. Run Application
* **Backend:**
  ```powershell
  uvicorn backend.app.main:app --reload --port 8000
  ```
* **Frontend:**
  ```powershell
  streamlit run frontend/app.py
  ```
