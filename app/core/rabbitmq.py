import json
import logging

import pika

from app.core.config import config_settings

logger = logging.getLogger("RabbitMQ-Util")

connection = None
channel = None

def get_connection():
    # Cloud RabbitMQ support
    if config_settings.RABBITMQ_URL:
        parameters = pika.URLParameters(
            config_settings.RABBITMQ_URL
        )

        return pika.BlockingConnection(parameters)

    # Local Docker RabbitMQ support
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config_settings.RABBITMQ_HOST,
            port=config_settings.RABBITMQ_PORT
        )
    )

def setup_queues(channel):
    # DLQ
    channel.queue_declare(queue=config_settings.DLQ_QUEUE, durable=True)

    # Main queue with DLQ config
    channel.queue_declare(
        queue=config_settings.JOB_QUEUE,
        durable=True,
        arguments={
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": config_settings.DLQ_QUEUE
        }
    )

def init_rabbitmq():
    global connection, channel

    connection = get_connection()
    channel = connection.channel()

    setup_queues(channel)

def ensure_channel():
    global connection, channel

    if connection is None or connection.is_closed:
        init_rabbitmq()

    elif channel is None or channel.is_closed:
        channel = connection.channel()
        setup_queues(channel)

def publish_job(job_id):
    global connection, channel

    message = json.dumps({"job_id": str(job_id)})

    try:
        ensure_channel()

        channel.basic_publish(
            exchange="",
            routing_key=config_settings.JOB_QUEUE,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2
            ),
        )

        logger.info(
            "Successfully published job %s to the queue.",
            job_id
        )

    except Exception:
        logger.exception(
            "Publish failed for job %s. Reconnecting...",
            job_id
        )

        try:
            init_rabbitmq()

            channel.basic_publish(
                exchange="",
                routing_key=config_settings.JOB_QUEUE,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2
                ),
            )

            logger.info(
                "Republish successful for job %s",
                job_id
            )

        except Exception:
            logger.exception(
                "Republish also failed for job %s",
                job_id
            )
            raise