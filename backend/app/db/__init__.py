import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and "supabase" in DATABASE_URL and "sslmode" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"

engine = create_engine(DATABASE_URL or "sqlite:///./cpaos_dev.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Optional dev bootstrap; production uses Alembic migrations."""
    # Import models so metadata is populated
    from app.models import onboarding  # noqa: F401

    if os.getenv("CPAOS_AUTO_CREATE_TABLES") == "1":
        Base.metadata.create_all(bind=engine)
