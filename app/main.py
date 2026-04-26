"""FastAPI application entry point."""
import logging
import threading

from fastapi import FastAPI

logger = logging.getLogger("Main")
from app.api.v1 import jobs, metrics
from app.core import rabbitmq
from app.core.logging import setup_logging
from app.db.session import Base, engine
from app.scheduler.scheduler import request_shutdown, run_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health-check")
def health_check():
    return {"status": "ok"}

app.include_router(jobs.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")

@app.on_event("startup")
def start_services():
    setup_logging()

    logger.info("Initialising RabbitMQ setup")
    rabbitmq.init_rabbitmq()

    logger.info("Starting scheduler thread...")
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()

@app.on_event("shutdown")
def shutdown_event():
    request_shutdown()
