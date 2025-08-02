# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies for psycopg2 (PostgreSQL adapter)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define environment variables
ENV PYTHONUNBUFFERED=1
ENV MODE=production

# Create entrypoint script
RUN echo '#!/bin/sh\n' \
    'set -e\n' \
    'python migrations/migrate.py\n' \
    'exec uvicorn Main:app --host 0.0.0.0 --port 8000' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]