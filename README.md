# Distributed Job Scheduler

A production-inspired distributed background job processing system built using **FastAPI**, **PostgreSQL**, and **RabbitMQ**.

The system is designed to handle asynchronous workloads reliably through queue-based execution, retry scheduling, worker scaling, failure recovery, and operational observability.

It is designed around engineering concerns such as concurrency, idempotency, horizontal scaling, exponential backoff retries, dead-letter handling, graceful shutdown, and safe state transitions.

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

The system accepts jobs through REST APIs, persists them in PostgreSQL, dispatches eligible jobs to message queue through a scheduler, and processes them asynchronously using a scalable worker pool connected via RabbitMQ.

It separates request handling from execution, allowing the API layer to remain responsive while workers process workloads independently.

---

## Core Capabilities

- Immediate and delayed job scheduling
- Asynchronous queue-driven execution
- Horizontally scalable worker pool
- Retry pipeline with exponential backoff
- Dead-letter handling for exhausted retries
- Explicit job lifecycle state management
- Recovery of stuck queued and running jobs
- Graceful shutdown for workers and scheduler
- Config-driven architecture
- Database-backed metrics endpoint
- Load tested under concurrent traffic and simulated failures

---

## Technology Stack

| Layer | Technology |
|------|------------|
| API Layer | FastAPI |
| Database | PostgreSQL |
| Queue / Broker | RabbitMQ |
| ORM | SQLAlchemy |
| Runtime | Python |
| Containerization | Docker Compose |

---

## System Architecture

> Replace this section with your custom architecture diagram image.

```text
Client Request
     ↓
FastAPI API Layer
     ↓
PostgreSQL (Jobs Table)
     ↓
Scheduler Poller
     ↓
RabbitMQ Queue
     ↓
Worker Pool (N Workers)
     ↓
Job Handlers
  - Email
  - Webhook
  - Log
```

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

## Reliability Design Decisions

### Durable Source of Truth

All jobs are persisted in PostgreSQL, allowing restart-safe recovery and metrics generation.

### Queue-Based Decoupling

RabbitMQ separates producers from consumers, allowing worker scaling without affecting API responsiveness.

### Duplicate Prevention through Idempotency

Explicit state transitions prevent the same job from being processed multiple times.

### Safe Concurrency

Database row locking with `FOR UPDATE SKIP LOCKED` avoids race conditions across concurrent schedulers/workers.

### Failure Recovery

Transient failures are retried automatically using exponential backoff scheduling.

### Stuck Job Recovery

Jobs left in `queued` or `running` state beyond threshold are detected and re-queued safely.

### Graceful Shutdown

Prevents message loss or abrupt worker termination.

---

## API Endpoints

### Jobs

| Method | Endpoint | Purpose |
|-------|----------|---------|
| POST | `/api/v1/jobs` | Create job |
| GET | `/api/v1/jobs` | List jobs |
| GET | `/api/v1/jobs/{id}` | Fetch single job |
| POST | `/api/v1/jobs/{id}/retry` | Retry job manually |
| POST | `/api/v1/jobs/{id}/cancel` | Cancel job |

### Monitoring

| Method | Endpoint | Purpose |
|-------|----------|---------|
| GET | `/api/v1/metrics` | System metrics |

---

## Example Metrics

```json
{
  "total_jobs_processed": 163,
  "success_jobs": 147,
  "failed_jobs": 15,
  "running_jobs": 0,
  "queued_jobs": 0,
  "pending_jobs": 0,
  "success_rate_percent": 90.18,
  "failure_rate_percent": 9.2,
  "jobs_retried": 48,
  "retry_recovery_rate_percent": 83.33,
  "avg_queue_wait_seconds": 0.54,
  "avg_processing_seconds": 0.01,
  "throughput_jobs_per_minute_last_hour": 0.08
}
```

---

## Validation / Load Testing

System behavior was validated under concurrent load and injected failures.

### Test Scenario

- 500 submitted jobs
- 7 parallel worker processes
- 30% simulated transient random failures
- Parallel bulk creation traffic

### Observed Results

- 98% final success rate after retries
- Balanced multi-worker consumption
- Automatic recovery of transient failures
- No duplicate job execution observed
- Stable queue draining under burst traffic

---
## Project Structure

```text
app/
  api/            REST endpoints
  core/           config, constants, logging, rabbitmq utils
  db/             engine + session
  db_utils/       CRUD + retry + scheduler DB operations
  handlers/       job handlers
  models/         SQLAlchemy models
  schemas/        request / response schemas
  scheduler/      polling scheduler
  services/       business logic
  worker/         queue consumer

scripts/
  bulk_create_jobs.py
```

---


## Run Locally

### 1. Clone Repository

```bash
git clone <repo-url>
open terminal in root directory
```

### 2. Add Configuration
Create a `.env` file in project root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/jobs_db
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672

JOB_QUEUE=job_queue
DLQ_QUEUE=job_dlq

SCHEDULER_POLL_INTERVAL=5
STUCK_JOB_TIMEOUT=60
MAX_FETCH_LIMIT=10

WORKER_PREFETCH_COUNT=1

DEFAULT_MAX_RETRIES=3
RETRY_BACKOFF_BASE=2

LOG_LEVEL=INFO
```

### 3. Start Infrastructure

```bash
docker-compose up -d
```

This starts:

- PostgreSQL container
- RabbitMQ container

### 4. Start API Server

```bash
uvicorn app.main:app --reload
```

### 5. Start Worker

```bash
python -c "from app.worker.worker import start_worker; start_worker()"
```

Run multiple terminals to scale workers horizontally.

---
## Key Concepts Demonstrated

- Distributed systems fundamentals
- Queue-based architecture
- Multi-threading / Multi-processing workers
- Concurrency control
- Idempotency
- Retry semantics
- Exponential backoff
- Dead Letter Queue pattern
- Fault recovery
- Graceful shutdown
- Operational observability
- Horizontal scaling

---

## Future Improvements

- Prometheus + Grafana dashboards
- Worker autoscaling
- Priority queues
- Per-handler rate limiting
- Admin dashboard UI
- Kubernetes deployment

---