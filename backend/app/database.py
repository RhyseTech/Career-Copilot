from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# For MVP, we will use SQLite if Postgres is unavailable
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("postgres"):
    # Simple fallback to sqlite for local dev without postgres
    DATABASE_URL = "sqlite:///./resumeiq.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
