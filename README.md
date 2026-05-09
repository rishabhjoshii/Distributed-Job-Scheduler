# Distributed Background Job Scheduler

A production-inspired distributed background job processing system built using **FastAPI**, **PostgreSQL**, and **RabbitMQ**.

The system supports asynchronous task execution through queue-based workers, retry scheduling, recurring jobs, failure recovery, and operational metrics.

It is designed around backend engineering concerns such as concurrency safety, at-least-once delivery semantics, exponential backoff retries, graceful shutdown, dead-letter handling, and scalable worker coordination.

---

## Problem Statement

Many backend systems need to process tasks that should not block API requests, such as:

- Sending emails
- Triggering webhooks
- Logging events
- Notifications
- Third-party integrations
- Scheduled background tasks

This project solves that problem by decoupling job creation from job execution.

---

## Overview

The system accepts jobs through REST APIs, persists them in PostgreSQL, dispatches eligible jobs to RabbitMQ through a scheduler, and processes them asynchronously using a scalable worker pool.

It separates request handling from execution, allowing the API layer to remain responsive while workers process workloads independently.

---

## Core Capabilities

- Immediate and delayed job scheduling
- Recurring interval-based schedules
- Asynchronous queue-driven execution
- Horizontally scalable worker pool
- Retry pipeline with exponential backoff
- Dead-letter handling for exhausted retries
- Explicit job lifecycle state management
- Recovery of stuck queued and running jobs
- Graceful shutdown for workers and scheduler
- Config-driven architecture
- Configurable API-key-based endpoint protection
- Database-backed metrics endpoint
- Load tested under concurrent traffic and simulated failures

---

## Technology Stack


| Layer            | Technology     |
| ---------------- | -------------- |
| API Layer        | FastAPI        |
| Database         | PostgreSQL     |
| Queue / Broker   | RabbitMQ       |
| ORM              | SQLAlchemy     |
| Runtime          | Python         |
| Containerization | Docker Compose |


---

## System Architecture

<p align="center">
  <img src="assets/architecture-diagram.png" alt="System Architecture" width="900"/>
</p>

---

## Job Lifecycle

```text
pending
   ↓
queued
   ↓
running
   ↓
success
```

Retry flow:

```text
running
   ↓
failure
   ↓
scheduled_at updated using backoff
   ↓
pending
   ↓
queued
   ↓
running
```

Terminal failure:

```text
max retries reached → failed / dead-letter queue
```

Optional cancellation:

```text
pending / queued → cancelled
```

---

## Durable Source of Truth

All jobs are persisted in PostgreSQL, allowing restart-safe recovery and metrics generation.

### Queue-Based Decoupling

RabbitMQ separates producers from consumers, allowing worker scaling without affecting API responsiveness.

### Idempotency and Safe State Transitions

Explicit job state transitions and database locking help prevent duplicate concurrent execution across workers.

### Safe Concurrency

Database row locking with `FOR UPDATE SKIP LOCKED` avoids race conditions across concurrent schedulers/workers.

### Failure Recovery

Transient failures are retried automatically using exponential backoff scheduling.

### Stuck Job Recovery

Jobs left in `queued` or `running` state beyond threshold are detected and re-queued safely.

### Graceful Shutdown

Workers and scheduler support graceful shutdown to reduce abrupt termination and message loss scenarios.

---

## Delivery Semantics

The system currently follows at-least-once delivery semantics.

Under certain failure scenarios (for example, worker crash after external side effect but before state persistence), a job may be re-processed. This tradeoff was intentionally accepted to keep the system architecture simpler and closer to common distributed queue patterns.

---

## API Endpoints

### API Endpoints

### Jobs


|        |                            |                    |
| ------ | -------------------------- | ------------------ |
| Method | Endpoint                   | Purpose            |
| POST   | `/api/v1/jobs`             | Create job         |
| GET    | `/api/v1/jobs`             | List jobs          |
| GET    | `/api/v1/jobs/{id}`        | Fetch single job   |
| POST   | `/api/v1/jobs/{id}/retry`  | Retry job manually |
| POST   | `/api/v1/jobs/{id}/cancel` | Cancel job         |


### Schedules


|        |                     |                           |
| ------ | ------------------- | ------------------------- |
| Method | Endpoint            | Purpose                   |
| POST   | `/api/v1/schedules` | Create recurring schedule |
| GET    | `/api/v1/schedules` | List schedules            |


### Monitoring


|        |                   |                |
| ------ | ----------------- | -------------- |
| Method | Endpoint          | Purpose        |
| GET    | `/api/v1/metrics` | System metrics |


---

## Authentication

Protected endpoints require an API key passed through the configured request header.

Example:

```
x-api-key: <your-api-key>
```

## Example Metrics

```json
{
  "total_jobs_processed": 500,
  "success_jobs": 492,
  "failed_jobs": 8,
  "running_jobs": 0,
  "queued_jobs": 0,
  "pending_jobs": 0,
  "success_rate_percent": 98.4,
  "failure_rate_percent": 1.6,
  "jobs_retried": 74,
  "retry_recovery_rate_percent": 89.19,
  "avg_queue_wait_seconds": 0.11,
  "avg_processing_seconds": 0.02,
  "throughput_jobs_per_minute": 327.5,
  "total_schedules": 25,
  "active_schedules": 0,
  "inactive_schedules": 25,
  "avg_runs_per_schedule": 20
}
```

---

## Validation / Load Testing

System behavior was validated under concurrent load, recurring scheduling scenarios, and injected failures.

### Test Scenario

- 500 concurrently submitted jobs and recurring schedules
- Multiple parallel worker processes
- Recurring interval schedules
- Simulated transient random failures
- Worker crash and recovery testing
- Parallel bulk creation traffic

### Observed Results

- Stable multi-worker queue consumption
- Automatic retry recovery for transient failures
- No duplicate concurrent execution observed
- Successful recurring schedule coordination
- Graceful worker recovery after partial failure
- Stable queue draining under burst traffic

---

---

## Project Structure

```text
app/
  api/            REST endpoints
  core/           config, constants, logging, rabbitmq utils
  db/             engine + session
  db_utils/       CRUD + retry + scheduler DB operations
  handlers/       job handlers
  middleware/     authentication middleware
  models/         SQLAlchemy models
  schemas/        request / response schemas
  scheduler/      polling scheduler
  services/       business logic
  worker/         queue consumer

scripts/
  bulk_create_jobs.py
  bulk_create_schedules.py
```

---

## Run Locally

### 1. Clone Repository

```bash
git clone <repo-url>
open terminal in root directory
```

### 2. Create Virtual Environment (Optional but Recommended)

#### macOS / Linux

```
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Add Configuration

Create a `.env` file in project root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/jobs_db 
DATABASE_POOL_SIZE=10 
DATABASE_POOL_MAX_OVERFLOW=20 

POSTGRES_USER=postgres 
POSTGRES_PASSWORD=postgres 
POSTGRES_DB=jobs_db 
POSTGRES_PORT=5432 

RABBITMQ_HOST=localhost 
RABBITMQ_PORT=5672 
RABBITMQ_MANAGEMENT_PORT=15672 

JOB_QUEUE=job_queue 
DLQ_QUEUE=job_dlq 

SCHEDULER_POLL_INTERVAL=5 
STUCK_JOB_TIMEOUT=60 
RECOVER_STUCK_LIMIT=50 
MAX_SCHEDULE_RUN_COUNT=10000 
MAX_FETCH_LIMIT=10 
WORKER_PREFETCH_COUNT=1 
DEFAULT_MAX_RETRIES=3 
RETRY_BACKOFF_BASE=2 

LOG_LEVEL=INFO 

EMAIL_PROVIDER=resend 
RESEND_API_KEY=<your-resend-api-key>
EMAIL_FROM=<your-email-registered-on-resend>

AUTH_ENABLED=true 
AUTH_API_KEYS=<auth-api-key>
AUTH_API_KEY_HEADER=x-api-key 
AUTH_SKIP_PATHS=/docs,/openapi.json,/favicon.ico,/health-check,/health,/metrics 
AUTH_PROTECTED_METHODS=GET,POST,PUT,PATCH,DELETE
```

### 5. Start Infrastructure

```bash
docker-compose up -d
```

This starts:

- PostgreSQL container
- RabbitMQ container

### 6. Start API Server

```bash
uvicorn app.main:app --reload
```

On first startup, required database tables are automatically created through SQLAlchemy metadata initialization.

The scheduler also starts automatically as part of the application startup lifecycle.

### 7. Start Worker

```bash
python -c "from app.worker.worker import start_worker; start_worker()"
```

Run multiple terminals to scale workers horizontally.

---

## Key Concepts Demonstrated

- Distributed systems fundamentals
- Queue-based architecture
- Multi-worker asynchronous execution
- Concurrency control
- Idempotency
- Retry semantics
- Exponential backoff
- Dead Letter Queue pattern
- Fault recovery
- Graceful shutdown
- Operational observability
- Horizontal scaling
- Scheduler-worker coordination

---

## Future Improvements

- Cron-based scheduling
- Prometheus + Grafana dashboards
- Priority queues
- Worker autoscaling
- Rate Limting
- Admin dashboard UI
- Multi-queue routing strategies

---

