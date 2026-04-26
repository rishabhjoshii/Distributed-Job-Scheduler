"""Database session management."""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from app.core.config import config_settings

DATABASE_URL = config_settings.DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_size=config_settings.DATABASE_POOL_SIZE,
    max_overflow=config_settings.DATABASE_POOL_MAX_OVERFLOW
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
