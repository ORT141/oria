FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (but NOT config.env — pass secrets at runtime!)
COPY . .

# Ensure instance directory exists for SQLite (dev only)
RUN mkdir -p instance

# Remove any accidentally-copied secrets
RUN rm -f config.env .env

EXPOSE 5001

# W-06 / C-04: Use Gunicorn in production, NOT flask run
# 4 sync workers, 120s timeout for AI-heavy endpoints
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "app:app"]
