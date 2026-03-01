# Agentic AI Platform Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/safe_workspace /app/chroma_db

# Set environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO
ENV SAFE_DIRECTORY=/app/safe_workspace
ENV CHROMA_DB_PATH=/app/chroma_db

# Expose API port
EXPOSE 8000

# Default command
CMD ["python", "main.py", "--api"]
