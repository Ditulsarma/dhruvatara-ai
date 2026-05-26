FROM python:3.11-slim-bookworm

# Install build dependencies + runtime libs for pyswisseph + Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libsqlite3-0 \
    libsqlite3-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (pyswisseph compiles from source)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright system deps + Chromium browser
RUN playwright install-deps chromium \
    && playwright install chromium

# Remove build-only deps to keep image small
RUN apt-get remove -y gcc python3-dev libsqlite3-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Create persistent data directory for SQLite (Railway volume mount)
RUN mkdir -p /data

# Pre-initialize database during build (idempotent - safe to run again at startup)
RUN python -c "from setup_db import setup_database; setup_database()"

# Make startup script executable
RUN chmod +x start.sh

# Expose port (Railway uses PORT env var, default 5000)
EXPOSE 5000

# Run startup script (initializes DB then starts gunicorn)
CMD ["./start.sh"]
