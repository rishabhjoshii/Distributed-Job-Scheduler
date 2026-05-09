import random
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

# PYTHONPATH=. python scripts/bulk_create_jobs.py
# run this command in the root directory of the project

API_URL = "http://localhost:8000/api/v1/jobs"

API_KEY = ""

TEST_TO_EMAIL = "email@gmail.com"
TEST_WEBHOOK_URL = "https://invalid-domain-test.com/webhook"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

TOTAL_JOBS = 50
MAX_PARALLEL_REQUESTS = 10

JOB_TYPES = ["log", "email", "webhook"]


def generate_payload(job_number):
    job_type = random.choice(JOB_TYPES)

    scheduled_at = (
        datetime.utcnow() +
        timedelta(seconds=random.randint(0, 5))
    ).isoformat()

    if job_type == "log":
        payload = {
            "message": f"Bulk log job {job_number}"
        }

    elif job_type == "email":
        payload = {
            "to": TEST_TO_EMAIL,
            "subject": f"Stress Test #{job_number}",
            "body": f"Email body for job {job_number}",
            "content_type": "text"
        }

    else:
        payload = {
            "url": TEST_WEBHOOK_URL,
            "method": "POST",
            "data": {
                "job_number": job_number,
                "message": f"Webhook test {job_number}"
            }
        }

    return {
        "type": job_type,
        "payload": payload,
        "scheduled_at": scheduled_at,
        "max_retries": random.choice([2, 3])
    }


def create_job(job_number):
    payload = generate_payload(job_number)

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=HEADERS,
            timeout=10
        )

        return {
            "job_number": job_number,
            "status_code": response.status_code,
            "success": response.status_code < 300,
            "response": response.json()
        }

    except Exception as e:
        return {
            "job_number": job_number,
            "success": False,
            "error": str(e)
        }


def main():
    print(f"\nCreating {TOTAL_JOBS} jobs...\n")

    start_time = time.time()

    results = []

    with ThreadPoolExecutor(
        max_workers=MAX_PARALLEL_REQUESTS
    ) as executor:

        futures = [
            executor.submit(create_job, i)
            for i in range(1, TOTAL_JOBS + 1)
        ]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            if result["success"]:
                print(
                    f"Job {result['job_number']:03d} | "
                    f"SUCCESS | "
                    f"Status={result['status_code']}"
                )
            else:
                print(
                    f"Job {result['job_number']:03d} | "
                    f"FAILED | "
                    f"{result.get('error') or result.get('response')}"
                )

    duration = time.time() - start_time

    total_success = sum(r["success"] for r in results)
    total_failed = len(results) - total_success

    print("\n========== SUMMARY ==========")
    print(f"Total Jobs      : {TOTAL_JOBS}")
    print(f"Successful      : {total_success}")
    print(f"Failed          : {total_failed}")
    print(f"Duration        : {duration:.2f}s")
    print(f"Req/sec         : {TOTAL_JOBS / duration:.2f}")
    print("=============================\n")


if __name__ == "__main__":
    main()