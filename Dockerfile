FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Optional build tools; most wheels are manylinux and won't need these,
# but keeping minimal tools can help if a wheel fallback builds.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (leverage Docker layer cache)
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install --only-binary=:all: -r requirements.txt || pip install -r requirements.txt

# Copy application code (including artifacts.pkl)
COPY . /app

EXPOSE 8000

# Use PORT provided by Render, default to 8000 locally
CMD ["sh", "-c", "uvicorn app:asgi_app --host 0.0.0.0 --port ${PORT:-8000}"]
