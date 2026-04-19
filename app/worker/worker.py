"""Worker logic."""
import json

from app.core import rabbitmq
from app.db.session import get_db_session
from app.db_utils.job_crud import get_job, handle_job_failure, update_job_status
from app.handlers import log_handler

def process_job(job_id):
    with get_db_session() as db:
        job = get_job(db, job_id)

        if not job:
            return

        try:
            log_handler.execute(job)
            update_job_status(db, job.id, "success")

        except Exception as e:
            handle_job_failure(db, job.id, e)

def callback(ch, method, properties, body):
    data = json.loads(body)
    job_id = data["job_id"]

    process_job(job_id)

    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    connection = rabbitmq.get_connection()
    channel = connection.channel()

    queue = channel.queue_declare(queue="job_queue", durable=True)

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue="job_queue",
        on_message_callback=callback
    )

    print("Worker started...")
    channel.start_consuming()