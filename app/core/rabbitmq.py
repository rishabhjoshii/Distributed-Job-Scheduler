import pika
import json


def get_connection():
    return pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )

def publish_job(job_id):
    connection = get_connection()
    channel = connection.channel()

    queue = channel.queue_declare(queue="job_queue", durable=True)

    message = json.dumps({"job_id": str(job_id)})

    channel.basic_publish(
        exchange="",
        routing_key="job_queue",
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2  # persistent
        ),
    )

    connection.close()