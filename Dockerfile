# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install system dependencies for psycopg2 AND Playwright
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    # Playwright dependencies
    wget \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and dependencies
RUN playwright install chromium && \
    playwright install-deps

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define environment variables
ENV PYTHONUNBUFFERED=1
ENV MODE=production

# Create entrypoint script (updated with Playwright check)
RUN echo '#!/bin/sh\n' \
    'set -e\n' \
    '# Verify Playwright browsers exist\n' \
    'if [ ! -d "/root/.cache/ms-playwright" ]; then\n' \
    '    playwright install chromium\n' \
    'fi\n' \
    '# Run migrations\n' \
    'python migrations/migrate.py\n' \
    '# Start the app\n' \
    'exec uvicorn Main:app --host 0.0.0.0 --port 8000' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]