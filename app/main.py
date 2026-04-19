"""FastAPI application entry point."""
import threading
from fastapi import FastAPI
from app.api.v1 import jobs
from app.core import rabbitmq
from app.db.session import Base, engine
from app.scheduler.scheduler import run_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health-check")
def health_check():
    return {"status": "ok"}

app.include_router(jobs.router, prefix="/api/v1")

@app.on_event("startup")
def start_scheduler():
    print("Initialising RabbitMQ setup")
    rabbitmq.init_rabbitmq()
    
    print("Starting scheduler thread...")
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
