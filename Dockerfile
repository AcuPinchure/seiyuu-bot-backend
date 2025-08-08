FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run gunicorn with increased header limits (src will be mounted at runtime)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--chdir", "/app/src", "--limit-request-line", "8190", "--limit-request-fields", "200", "--limit-request-field_size", "16380", "lovelive_seiyuu_bot_backend.wsgi:application"]