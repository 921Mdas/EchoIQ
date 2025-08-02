#!/bin/sh

# Run migrations
python migrations/migrate.py

# Start application
exec uvicorn Main:app --host 0.0.0.0 --port 8000