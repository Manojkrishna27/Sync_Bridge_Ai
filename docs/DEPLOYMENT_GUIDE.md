# SyncBridge AI Integration Gateway - Production Deployment Guide

This guide details the deployment, DevOps, and security hardening procedures for running SyncBridge AI Integration Gateway in production environments.

---

## 1. Production Architecture Overview

The system uses a multi-container Docker topology managed via Docker Compose or Kubernetes:

```
Internet ──► Nginx Reverse Proxy (SSL, Compression, Rate Limits)
                 │
                 ├──► Frontend Single Page App (Static Assets)
                 └──► Backend Flask API Gateway (Gunicorn WSGI)
                          │
                          ├──► MySQL 8.0 (Relational Data & Audit Logs)
                          └──► Redis 7.0 (Cache, Rate Limits & Vector Store)
```

---

## 2. Quickstart Production Deployment

### Prerequisites
- Docker Engine `v20.10+` and `docker compose` plugin.
- SSL Certificate (`fullchain.pem` and `privkey.pem`) if enabling HTTPS.

### Steps
1. Clone Repository & Environment Setup:
   ```bash
   git clone https://github.com/syncbridge/syncbridge-ai-gateway.git
   cd syncbridge-ai-gateway
   ```

2. Configure Production Environment:
   ```bash
   cp .env.example .env
   ```

3. Launch Production Stack:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

4. Verify Services Health:
   ```bash
   docker compose -f docker-compose.prod.yml ps
   curl -i http://localhost/healthz
   ```

---

## 3. Disaster Recovery & Backup

### Automated Daily Database Backup
Run the backup script:
```bash
./scripts/backup.sh
```

### Database Restore Procedure
Restore from a SQL snapshot:
```bash
./scripts/restore.sh ./backups/mysql_backup_YYYYMMDD_HHMMSS.sql
```
