set shell := ["bash", "-cu"]

# Create virtual environment
setup:
    python3 -m venv venv
    venv/bin/pip install -r requirements.txt

# Install dependencies
install:
    venv/bin/pip install -r requirements.txt

# Run docker + FastAPI app
start-server:
    docker-compose up -d
    venv/bin/uvicorn app.main:app --reload

# fastapi app
run:
    venv/bin/uvicorn app.main:app --reload

# start Docker Container
docker-up:
    docker-compose up -d


