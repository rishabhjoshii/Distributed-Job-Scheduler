"""FastAPI application entry point."""
import logging
import threading

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.core.auth_middleware import auth_api_key_middleware
from app.core.config import config_settings
import app.db
from app.api.v1 import jobs, metrics, schedules
from app.core import rabbitmq
from app.core.logging import setup_logging
from app.db.session import Base, engine
from app.scheduler.scheduler import request_shutdown, run_scheduler
from app.worker.worker import start_worker

logger = logging.getLogger("Main")

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.middleware("http")(auth_api_key_middleware)

@app.get("/health-check")
def health_check():
    return {"status": "ok"}

app.include_router(jobs.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")

@app.on_event("startup")
def start_services():
    setup_logging()

    logger.info("Initialising RabbitMQ setup")
    rabbitmq.init_rabbitmq()

    if config_settings.START_SCHEDULER_ON_API_STARTUP:
        logger.info("Starting scheduler thread...")

        scheduler_thread = threading.Thread(
            target=run_scheduler,
            daemon=True
        )
        scheduler_thread.start()

    if config_settings.START_WORKER_ON_API_STARTUP:
        logger.info("Starting worker thread...")

        worker_thread = threading.Thread(
            target=start_worker,
            daemon=True
        )
        worker_thread.start()

@app.on_event("shutdown")
def shutdown_event():
    request_shutdown()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Distributed Job Scheduler",
        version="1.0.0",
        description="API documentation",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": config_settings.AUTH_API_KEY_HEADER
        }
    }

    openapi_schema["security"] = [{"ApiKeyAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
