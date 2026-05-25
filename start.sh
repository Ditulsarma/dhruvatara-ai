#!/bin/sh
set -e

echo "=== Dhruvatara AI Startup ==="
echo "Python version: $(python --version)"
echo "Working dir: $(pwd)"
echo "Files in /app: $(ls -la)"

# Run database setup before starting the app
echo "Initializing database..."
python -c "from setup_db import setup_database; setup_database(); print('DB ready.')" 2>&1

echo "Verifying app can be imported..."
python -c "from app import app; print('App import OK. Routes:', len(app.url_map._rules))" 2>&1

echo "Starting gunicorn on port ${PORT:-5000}..."
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers 1 --timeout 120 --log-level debug --access-logfile - --error-logfile - wsgi:app