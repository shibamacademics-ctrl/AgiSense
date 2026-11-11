FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/Backend \
    PORT=10000

WORKDIR /app

# Install minimal OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy Backend codebase
COPY Backend ./Backend

# Copy Model weights and metadata
COPY ["Crop Recommendation Train Output", "./Crop Recommendation Train Output"]
COPY ["Yield Train Output", "./Yield Train Output"]
COPY ["Disease Detection Output", "./Disease Detection Output"]

EXPOSE 10000

# Start Uvicorn bound to 0.0.0.0 and dynamic $PORT
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000} --app-dir /app/Backend"]
