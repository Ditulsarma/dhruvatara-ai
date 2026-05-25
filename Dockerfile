FROM python:3.11-slim

# Install build dependencies + runtime libs for pyswisseph
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

# Remove build deps to keep image small
RUN apt-get remove -y gcc python3-dev libsqlite3-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Expose port (Railway uses PORT env var, default 5000)
EXPOSE 5000

# Run with gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 app:app"]
