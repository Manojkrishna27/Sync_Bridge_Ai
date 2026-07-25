# Multi-stage Backend Dockerfile
FROM python:3.10-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final Production Image
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Add unprivileged user for security hardening
RUN groupadd -r syncuser && useradd -r -g syncuser syncuser

COPY --from=builder /root/.local /home/syncuser/.local
COPY . .

# Set permissions
RUN chown -R syncuser:syncuser /app /home/syncuser/.local

ENV PATH=/home/syncuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

USER syncuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/v1/health || exit 1

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "wsgi:app"]
