FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make port configurable via environment variable
ENV PORT=8001
EXPOSE $PORT

# Use environment variable for port
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
