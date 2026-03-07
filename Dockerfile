# ---------- Base image ----------
FROM python:3.9-slim

# Avoid writing .pyc, ensure logs are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System-level deps (if you later need gcc or libgomp for ML, add here)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Expose Flask/Gunicorn port
EXPOSE 8000

# Start via Gunicorn (module:app)
# If your entrypoint changes, update 'app:app' accordingly
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app", "--workers", "3", "--timeout", "90"]