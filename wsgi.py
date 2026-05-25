"""
WSGI entry point for Dhruvatara AI.
Used by gunicorn on Railway.
"""
from app import app

# This allows: gunicorn wsgi:app
if __name__ == "__main__":
    app.run()
