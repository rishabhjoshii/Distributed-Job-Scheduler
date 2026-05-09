import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# PYTHONPATH=. python scripts/bulk_create_schedules.py
# run this command in the root directory of the project

API_URL = "http://localhost:8000/api/v1/schedules"

HEADERS = {
    "x-api-key": "",
    "Content-Type": "application/json"
}

TOTAL_SCHEDULES = 10
MAX_PARALLEL_REQUESTS = 5


def create_schedule(schedule_number):
    payload = {
        "type": "log",
        "payload": {
            "message": f"Recurring schedule #{schedule_number}"
        },
        "schedule_type": "interval",
        "schedule_config": {
            "interval_seconds": 5
        },
        "max_runs": 10
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=HEADERS,
            timeout=10
        )

        return {
            "schedule_number": schedule_number,
            "success": response.status_code < 300,
            "status_code": response.status_code,
            "response": response.json()
        }

    except Exception as e:
        return {
            "schedule_number": schedule_number,
            "success": False,
            "error": str(e)
        }


def main():
    print(f"\nCreating {TOTAL_SCHEDULES} recurring schedules...\n")

    start = time.time()

    results = []

    with ThreadPoolExecutor(
        max_workers=MAX_PARALLEL_REQUESTS
    ) as executor:

        futures = [
            executor.submit(create_schedule, i)
            for i in range(1, TOTAL_SCHEDULES + 1)
        ]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            if result["success"]:
                print(
                    f"Schedule {result['schedule_number']:02d} | "
                    f"SUCCESS | "
                    f"Status={result['status_code']}"
                )
            else:
                print(
                    f"Schedule {result['schedule_number']:02d} | "
                    f"FAILED | "
                    f"{result.get('error') or result.get('response')}"
                )

    duration = time.time() - start

    total_success = sum(r["success"] for r in results)
    total_failed = len(results) - total_success

    print("\n========== SUMMARY ==========")
    print(f"Total Schedules : {TOTAL_SCHEDULES}")
    print(f"Successful      : {total_success}")
    print(f"Failed          : {total_failed}")
    print(f"Duration        : {duration:.2f}s")
    print("=============================\n")


if __name__ == "__main__":
    main()