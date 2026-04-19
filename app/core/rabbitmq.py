import json
import logging

import pika

logger = logging.getLogger("RabbitMQ-Util")

connection = None
channel = None

def get_connection():
    return pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )

def setup_queues(channel):
    # DLQ
    channel.queue_declare(queue="job_dlq", durable=True)

    # Main queue with DLQ config
    channel.queue_declare(
        queue="job_queue",
        durable=True,
        arguments={
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": "job_dlq"
        }
    )

def init_rabbitmq():
    global connection, channel

    connection = get_connection()
    channel = connection.channel()

    setup_queues(channel)

def publish_job(job_id):
    message = json.dumps({"job_id": str(job_id)})

    channel.basic_publish(
        exchange="",
        routing_key="job_queue",
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2  # persistent
        ),
    )
    logger.info("Successfully published job %s to the queue.", job_id)