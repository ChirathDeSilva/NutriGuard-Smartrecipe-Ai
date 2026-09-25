import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Ensure backend/data directory exists for the SQLite database
DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)

# Read DATABASE_URL from environment or fallback to standard SQLite path
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_DIR / 'recipes.db'}")

# SQLite requires 'check_same_thread: False' to allow multi-threaded access in FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Database SessionLocal for queries
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields an independent database session
    per request and ensures clean closing upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
