# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables for Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    DEBIAN_FRONTEND=noninteractive \
    PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Install system dependencies in a single RUN layer
RUN apt-get update && apt-get install -y \
    # General dependencies
    libpq-dev \
    gcc \
    # Playwright dependencies
    wget \
    # Core browser dependencies
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
    # ARM-specific dependencies
    libcups2 \
    libcairo2 \
    libpango-1.0-0 \
    libjpeg62-turbo \
    libgdk-pixbuf-2.0-0 \
    fonts-freefont-ttf \
    fonts-noto-color-emoji \
    fonts-liberation \
    fonts-droid-fallback \
    fonts-unifont \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir bcrypt==4.0.1 passlib==1.7.4 \
    && pip install playwright==1.40.0

# Install spaCy language models
RUN python -m spacy download en_core_web_sm \
    && python -m spacy download fr_core_news_sm

# Install Playwright browsers manually for ARM
RUN playwright install chromium

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    MODE=production

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health || exit 1

# Create entrypoint script
RUN echo '#!/bin/sh\n' \
    'set -e\n\n' \
    '# Verify dependencies\n' \
    'playwright install chromium\n' \
    'python -m spacy download en_core_web_sm || true\n' \
    'python -m spacy download fr_core_news_sm || true\n\n' \
    '# Run migrations\n' \
    'python migrations/migrate.py\n\n' \
    '# Start the app\n' \
    'exec uvicorn Main:app --host 0.0.0.0 --port 8000' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]