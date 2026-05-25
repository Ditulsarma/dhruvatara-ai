#!/bin/sh

echo "=== Dhruvatara AI Startup ==="
echo "Python: $(python --version)"
echo "PWD: $(pwd)"
echo "Files: $(ls)"

echo "--- DB Init ---"
python -c "from setup_db import setup_database; setup_database(); print('OK')" || echo "DB init had issues but continuing..."

echo "--- Import Test ---"
python -c "from app import app; print('OK, routes:', len(app.url_map._rules))" || echo "Import test had issues but continuing..."

echo "--- Starting Gunicorn on ${PORT:-5000} ---"
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" --workers 1 --timeout 120 --log-level debug --access-logfile - --error-logfile - wsgi:app