# Backend Dockerfile (FastAPI)
FROM python:3.12-slim
LABEL "language"="python"
LABEL "framework"="fastapi"

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Backend Code
COPY . .

# NOTE: Static files are no longer served from Python in the split architecture.
# But we keep the directory structure compatible.

# Create /data directory for persistent storage
RUN mkdir -p /data

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
