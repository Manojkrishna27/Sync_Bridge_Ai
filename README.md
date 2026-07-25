# 🌐 SyncBridge AI Integration Gateway

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/react-18.0%2B-61dafb.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/docker-compose-2496ed.svg)](https://www.docker.com/)
[![MySQL](https://img.shields.io/badge/mysql-8.0-4479a1.svg)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/redis-7.0-dc382d.svg)](https://redis.io/)
[![Tests](https://img.shields.io/badge/tests-29%2F29%20passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

**SyncBridge AI** is an enterprise-grade, multi-tenant integration middleware platform and AI Copilot gateway. Built with Flask, React, MySQL, Redis, Nginx, Docker, and a specialized Multi-Agent RAG layer, SyncBridge AI seamlessly connects disparate enterprise software systems (REST, SOAP, gRPC, SFTP, XML, CSV, JSON), automates complex schema transformations, and provides real-time intelligent monitoring.

---

## 🚀 Key Features

### 🔌 Multi-Protocol Transformation Engine
- **Universal Connectors**: Native support for **REST**, **SOAP**, **gRPC**, **SFTP**, **XML**, **CSV**, and **JSON**.
- **Transformation Pipeline**: Dynamic payload parsing, schema validation, field mapping rules engine, and bidirectionally transformed response generation.

### 🤖 AI Schema Intelligence & Multi-Agent Workbench
- **Visual Mapping Studio**: Interactive UI for drag-and-drop and AI-assisted source-to-target field mapping.
- **Automated Mapping Generator**: Uses LLM intelligence to match complex nested schemas across different protocols.
- **RAG & Hybrid Search Engine**: Powered by BM25 keyword matching, vector embeddings, and Reciprocal Rank Fusion (RRF) for context-aware developer assist.

### 💬 Multi-Agent Copilot & Real-Time SSE
- **Specialized AI Agents**: 
  - `SchemaAgent` - Analyzes structure and data type compliance.
  - `MappingAgent` - Generates transformation logic.
  - `TroubleshootingAgent` - Diagnoses integration execution failures.
  - `PerformanceAgent` - Recommends latency & caching optimizations.
  - `ConnectorAgent` & `DocumentationAgent` - Automated connector code generation & docs.
- **Server-Sent Events (SSE)**: Stream Copilot responses in real-time directly to the React frontend.

### 🛡️ Enterprise Security & Multi-Tenant Control
- **Authentication & RBAC**: JWT authentication with granular multi-tenant role-based permissions (`Admin`, `Developer`, `Auditor`).
- **API Key Security**: Cryptographically hashed tenant API keys with scope restrictions.
- **Audit Logging**: Immutable, queryable audit trail covering all system and security events.

### ⚡ Caching, Rate Limiting & Monitoring
- **Multi-Tier Redis Caching**: Namespace-isolated sliding expiration with payload compression.
- **Sliding-Window Rate Limiter**: IP and Tenant API-key based rate limiting via Redis.
- **Observability**: Real-time Prometheus metric exposition (`/api/v1/monitoring/prometheus`) and system health diagnostics.

---

## 🏗️ System Architecture

```
                  ┌────────────────────────────────────────────────────────┐
                  │              Nginx Reverse Proxy & Load Balancer       │
                  │        (SSL, HSTS, CSP, Gzip, HTTP 429 Rate Limits)    │
                  └───────────────────────────┬────────────────────────────┘
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     ▼                                                 ▼
        ┌─────────────────────────┐                       ┌─────────────────────────┐
        │  React SaaS Frontend    │                       │  Flask WSGI Gateway     │
        │ (Vite, Tailwind, Flow)  │                       │ (Gunicorn, Clean Arch)  │
        └─────────────────────────┘                       └────────────┬────────────┘
                                                                       │
           ┌──────────────────────┬──────────────────────┬─────────────┴────────┬──────────────────────┐
           ▼                      ▼                      ▼                      ▼                      ▼
  ┌─────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
  │  Multi-Tenant   │   │  Integration     │   │  Multi-Agent AI  │   │  Monitoring &    │   │ Redis Cache &    │
  │  Client Service │   │  Engine & Rules  │   │  Copilot & RAG   │   │  Observability   │   │ Rate Limiter     │
  └────────┬────────┘   └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘
           │                     │                      │                      │                      │
           └─────────────────────┴──────────────────────┼──────────────────────┴──────────────────────┘
                                                        ▼
                                       ┌──────────────────────────────────┐
                                       │     MySQL 8.0 Relational DB      │
                                       │ (Schematic Storage & Audit Logs) │
                                       └──────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18 (JSX), Vite, TailwindCSS, Lucide Icons, Axios |
| **Backend API** | Python 3.10, Flask 3.0, Flask-RESTX (Swagger), SQLAlchemy ORM, Gunicorn WSGI |
| **Data & Caching** | MySQL 8.0, Redis 7.0 (Sliding Expiration, Compression, Tags) |
| **AI & RAG** | Multi-Agent Orchestrator, Vector Store, BM25 Search, RRF Reranking |
| **DevOps & Infra** | Docker, Docker Compose, Nginx, GitHub Actions CI/CD, Prometheus Metrics |

---

## 📁 Repository Structure

```
SyncBridge_AI/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # RESTX Controllers (Auth, Clients, Integrations, Copilot, etc.)
│   │   ├── ai/              # Multi-Agent Framework, RAG Pipeline, Tools & Prompts
│   │   ├── connectors/      # Pluggable Protocol Connectors (REST, SOAP, gRPC, SFTP, etc.)
│   │   ├── core/            # Config, Extensions, Security, Caching, Rate Limiter
│   │   ├── integration_engine/ # Payload Parser, Rules Engine, Transformation Engine
│   │   ├── models/          # SQLAlchemy ORM Data Models
│   │   ├── repositories/    # Clean Architecture Repositories
│   │   └── services/        # Core Business Logic Services
│   ├── tests/               # Pytest Automated Test Suites
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # UI Layouts & Common Modals
│   │   ├── pages/           # Visual Studio, Playground, Copilot, Monitoring, etc.
│   │   └── services/        # Axios API Client
│   └── Dockerfile
├── docker/                  # Nginx Configurations & Dockerfiles
├── docs/                    # Production DevOps & Deployment Documentation
├── scripts/                 # Backup and Disaster Recovery Shell Scripts
├── docker-compose.yml       # Local Development Compose File
├── docker-compose.prod.yml  # Production Topology Compose File
└── README.md
```

---

## ⚡ Quickstart Guide

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) `v20.10+` and `docker compose`
- [Python 3.10+](https://www.python.org/) *(Optional for local dev without Docker)*
- [Node.js 18+](https://nodejs.org/) *(Optional for local dev without Docker)*

---

### Running with Docker Compose (Recommended)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Manojkrishna27/Sync_Bridge_Ai.git
   cd Sync_Bridge_Ai
   ```

2. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   ```

3. **Launch Stack**:
   - **Production Mode**:
     ```bash
     docker compose -f docker-compose.prod.yml up -d --build
     ```
   - **Development Mode**:
     ```bash
     docker compose -f docker-compose.dev.yml up -d --build
     ```

4. **Access the Services**:
   - 🌐 **Frontend Application**: `http://localhost`
   - ⚡ **Backend API**: `http://localhost/api/v1`
   - 📚 **Swagger Documentation**: `http://localhost/api/v1/docs`
   - 📊 **Prometheus Metrics**: `http://localhost/api/v1/monitoring/prometheus`

---

## 🧪 Running Automated Tests

The repository includes **29 comprehensive test suites** covering multi-protocol transformations, AI mapping rules, caching, rate limiting, and RBAC authentication.

To run the full test suite locally:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/ -v
```

Expected Output:
```text
============================= test session starts ==============================
collected 29 items

backend/tests/test_integration_engine.py ......                        [ 20%]
backend/tests/test_milestone3.py ....                                  [ 34%]
backend/tests/test_milestone5.py .....                                 [ 51%]
backend/tests/test_milestone6.py .....                                 [ 68%]
backend/tests/test_milestone7.py .....                                 [ 86%]
backend/tests/test_milestone8.py ....                                 [100%]

======================== 29 passed, 2 warnings in 4.17s ========================
```

---

## 💾 Disaster Recovery & Backups

Automated database maintenance scripts are located in the `scripts/` directory:

- **Create a MySQL Backup**:
  ```bash
  ./scripts/backup.sh
  ```
  *Backups are saved to `./backups/mysql_backup_YYYYMMDD_HHMMSS.sql`.*

- **Restore from Backup**:
  ```bash
  ./scripts/restore.sh ./backups/mysql_backup_YYYYMMDD_HHMMSS.sql
  ```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Manojkrishna27/Sync_Bridge_Ai/issues).

---

<p center="align">Built with ❤️ for enterprise integration and AI orchestration.</p>
