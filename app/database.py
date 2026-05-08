# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Simple SQLite URL for development
SQLALCHEMY_DATABASE_URL = "sqlite:///./bizlink.db"


# Create engine with SQLite-specific thread safety arg
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# Session factory for database interactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for ORM models
Base = declarative_base()


# Database session dependency (kept here as requested)
def get_db():
    """Dependency: Provide a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()