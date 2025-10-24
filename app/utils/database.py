# app/utils/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# use env var if present, otherwise your local MySQL URL
# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "mysql+pymysql://sameerbangkokumeed:Sameer1313umeed@localhost/astro_schemas"
# )

# ✅ MySQL Database URL
DATABASE_URL = "mysql+pymysql://root:office1234@localhost/astro_schemas"
#DATABASE_URL = "mysql+pymysql://sameerbangkokumeed:Sameer1313umeed@localhost/astro_schemas"

# Example:
# DATABASE_URL = "mysql+pymysql://root:password123@localhost/templamart"


# Example:
# DATABASE_URL = "mysql+pymysql://root:password123@localhost/templamart"
# engine configuration (sensible defaults)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=True,
)

# session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# THE Base object used by all models
Base = declarative_base()

def get_db():
    """FastAPI dependency: yield a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Create tables for all models registered on Base.metadata.
    IMPORTANT: import your models (e.g. `import app.models.models`) BEFORE calling this,
    so model classes are attached to Base.metadata.
    """
    Base.metadata.create_all(bind=engine)
