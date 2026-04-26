import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import random

API_URL = "http://localhost:8000/api/v1/jobs"

TOTAL_JOBS = 100
MAX_PARALLEL_REQUESTS = 20

JOB_TYPES = ["log", "email", "webhook"]


def create_job(job_number):
    delay_seconds = random.randint(0, 5)

    scheduled_at = (
        datetime.utcnow() + timedelta(seconds=delay_seconds)
    ).isoformat()

    payload = {
        "type": random.choice(JOB_TYPES),
        "payload": {
            "job_number": job_number,
            "message": f"Bulk Job {job_number}"
        },
        "scheduled_at": scheduled_at,
        "max_retries": random.choice([2, 3])
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=10)

        return (
            job_number,
            response.status_code,
            response.json()
        )

    except Exception as e:
        return (
            job_number,
            "ERROR",
            str(e)
        )


def main():
    print(f"Creating {TOTAL_JOBS} jobs...\n")

    with ThreadPoolExecutor(
        max_workers=MAX_PARALLEL_REQUESTS
    ) as executor:

        futures = [
            executor.submit(create_job, i)
            for i in range(1, TOTAL_JOBS + 1)
        ]

        for future in as_completed(futures):
            job_number, status, result = future.result()

            print(
                f"Job {job_number:02d} | "
                f"Status: {status} | "
                f"Result: {result}"
            )


if __name__ == "__main__":
    main()