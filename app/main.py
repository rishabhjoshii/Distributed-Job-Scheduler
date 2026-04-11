"""FastAPI application entry point."""
from fastapi import FastAPI
from app.api.v1 import jobs
from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health-check")
def health_check():
    return {"status": "ok"}

app.include_router(jobs.router, prefix="/api/v1")
