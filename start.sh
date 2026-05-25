#!/bin/sh
set -e

echo "=== Dhruvatara AI Startup ==="

# Run database setup before starting the app
echo "Initializing database..."
python -c "from setup_db import setup_database; setup_database(); print('DB ready.')"

echo "Verifying app can be imported..."
python -c "from app import app; print('App import OK.')"

echo "Starting gunicorn..."
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers 1 --timeout 120 --preload --log-level info --access-logfile - --error-logfile - wsgi:app