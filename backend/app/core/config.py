"""
CORE CONFIGURATION
==================
Centralized environment configuration management using python-dotenv.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "nutriguard_default_dev_secret_key_2026")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'backend' / 'data' / 'recipes.db'}")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
USDA_API_KEY = os.getenv("USDA_API_KEY", "")
THEMEALDB_API_KEY = os.getenv("THEMEALDB_API_KEY", "1")
