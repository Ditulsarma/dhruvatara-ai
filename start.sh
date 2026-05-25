#!/bin/sh
set -e

echo "=== Dhruvatara AI Startup ==="

# Run database setup before starting the app
echo "Initializing database..."
python -c "from setup_db import setup_database; setup_database(); print('DB ready.')"

echo "Starting gunicorn..."
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers 2 --timeout 120 --log-level info --access-logfile - --error-logfile - app:app