FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including ffprobe
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml poetry.lock* requirements.txt* ./

# Install Poetry and dependencies
RUN pip install --no-cache-dir poetry

# Configure poetry: don't create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (including dev dependencies for hot reload)
RUN poetry install --no-root

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]