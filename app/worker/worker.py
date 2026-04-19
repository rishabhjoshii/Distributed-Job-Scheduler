"""Worker logic."""
from datetime import datetime
import json
import logging

from app.core import rabbitmq
from app.core.constants import JobState
from app.core.logging import setup_logging
from app.db.session import get_db_session
from app.db_utils.job_crud import fetch_job_for_update, get_job, handle_job_failure, update_job_status
from app.handlers import log_handler
from app.core.metrics import metrics
import time

logger = logging.getLogger("Worker")


def process_job(db, job_id):
    logger.info(f"Processing job {job_id}")
    job = fetch_job_for_update(db, job_id)

    if not job:
        return "not_found", None

    # Idempotency check -> jobId + jobstatus behaving idempotency key for us
    if job.status == JobState.SUCCESS:
        return "already_processed", None

    if job.status == JobState.RUNNING:
        return "in_progress", None

    job.status = JobState.RUNNING
    job.started_at = datetime.utcnow()
    db.commit()

    start_time = time.time()
    try:
        log_handler.execute(job)
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

        if status in ["success", "already_processed", "in_progress"]:
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

    connection = rabbitmq.get_connection()
    channel = connection.channel()

    rabbitmq.setup_queues(channel)

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue="job_queue",
        on_message_callback=callback
    )

    logger.info("Worker started...")
    channel.start_consuming()