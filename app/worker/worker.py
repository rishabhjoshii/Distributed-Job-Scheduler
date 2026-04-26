"""Worker logic."""
from datetime import datetime
import json
import logging
import signal
import time
from app.core import rabbitmq
from app.core.config import config_settings
from app.core.constants import JobState, normalize_value
from app.core.logging import setup_logging
from app.db.session import get_db_session
from app.db_utils.job_crud import fetch_job_for_update, get_job, handle_job_failure, update_job_status
from app.core.metrics import metrics
from app.handlers.registry import get_job_handler

logger = logging.getLogger("Worker")
shutdown_requested = False
channel = None
connection = None

def handle_shutdown(signum, frame):
    global shutdown_requested

    logger.info("Shutdown signal received...")
    shutdown_requested = True

    if channel and channel.is_open:
        channel.stop_consuming()

def process_job(db, job_id):
    logger.info(f"Processing job {job_id}")
    job = fetch_job_for_update(db, job_id)

    if not job:
        return "not_found", None

    # Idempotency check -> jobId + jobstatus behaving idempotency key for us
    if normalize_value(job.status) != JobState.QUEUED.value:
        logger.warning(
            "Ignoring job %s in unexpected state %s",
            job.id,
            job.status
        )
        return "invalid_state", None

    job.status = JobState.RUNNING
    job.started_at = datetime.utcnow()
    db.commit()

    start_time = time.time()
    try:
        job_type = normalize_value(job.type)
        handler = get_job_handler(job_type)

        if not handler:
            raise ValueError(f"Unsupported job type {job.type}")

        handler.execute(job)

        update_job_status(db, job.id, JobState.SUCCESS)
        metrics.jobs_processed += 1
        return "success", None

    except Exception as e:
        handle_job_failure(db, job.id, e)
        metrics.jobs_failed += 1
        return "failed", e

    finally:
        duration = time.time() - start_time
        logger.info(f"Job {job.id} took {duration:.2f}s")

def callback(ch, method, properties, body):
    data = json.loads(body)
    job_id = data["job_id"]

    with get_db_session() as db:
        try:
            job = get_job(db, job_id)
        except ValueError:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        status, error = process_job(db, job.id)
        db.refresh(job)

        if status in ["success", "invalid_state", "not_found"]:
            ch.basic_ack(delivery_tag=method.delivery_tag)

        else:
            if job.retry_count >= job.max_retries:
                # send to DLQ
                ch.basic_nack(
                    delivery_tag=method.delivery_tag,
                    requeue=False
                )
                logger.error("Job %s added to DLQ. Error: %s", job.id, error)
            else:
                # retry
                ch.basic_ack(delivery_tag=method.delivery_tag)


def start_worker():
    setup_logging()

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    global channel, connection

    connection = rabbitmq.get_connection()
    channel = connection.channel()

    rabbitmq.setup_queues(channel)

    channel.basic_qos(prefetch_count=config_settings.WORKER_PREFETCH_COUNT)

    channel.basic_consume(
        queue=config_settings.JOB_QUEUE,
        on_message_callback=callback
    )

    try:
        logger.info("Worker started...")
        channel.start_consuming()
    finally:
        logger.info("Closing worker resources...")

        if channel.is_open:
            channel.close()

        if connection.is_open:
            connection.close()

        logger.info("Worker shutdown complete")