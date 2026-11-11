# ==========================================
# Stage 1: Build the Vite React Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/Frontend

# Install dependencies
COPY Frontend/package*.json ./
RUN npm ci || npm install

# Build production assets
COPY Frontend/ ./
RUN npm run build

# ==========================================
# Stage 2: Production Python API + Static UI
# ==========================================
FROM python:3.11-slim AS runner

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/Backend \
    PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code, database migrations, and model weights
COPY Backend ./Backend
COPY ["Crop Recommendation Train Output", "./Crop Recommendation Train Output"]
COPY ["Yield Train Output", "./Yield Train Output"]
COPY ["Disease Detection Output", "./Disease Detection Output"]

# Copy built frontend from Stage 1 into the static directory
COPY --from=frontend-builder /app/Frontend/dist ./Frontend/dist

# Expose container port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start Uvicorn bound to 0.0.0.0 and dynamic $PORT
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --app-dir /app/Backend"]
