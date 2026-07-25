# SyncBridge AI

**Enterprise-grade multi-tenant integration middleware & AI Copilot gateway**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-black.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-29%20passed-brightgreen.svg)](#running-tests)

SyncBridge AI connects disparate enterprise systems (REST, SOAP, gRPC, SFTP, XML, CSV, JSON), automates complex schema transformations, and delivers a real-time multi-agent AI Copilot for developers and integration engineers.

---

## Table of Contents

- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Running Tests](#running-tests)
- [Disaster Recovery](#disaster-recovery)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Key Features

### Multi-Protocol Transformation Engine
- **Universal Connectors** — Native support for REST, SOAP, gRPC, SFTP, XML, CSV, and JSON
- **Transformation Pipeline** — Dynamic payload parsing, schema validation, field-mapping rules engine, and bidirectional response generation

### AI Schema Intelligence & Multi-Agent Workbench
- **Visual Mapping Studio** — Interactive drag-and-drop + AI-assisted source-to-target field mapping
- **Automated Mapping Generator** — LLM-powered matching of complex nested schemas across protocols
- **RAG & Hybrid Search** — BM25 + vector embeddings + Reciprocal Rank Fusion (RRF) for context-aware developer assist

### Multi-Agent Copilot & Real-Time SSE
Specialized agents that collaborate on integration tasks:

| Agent                | Responsibility                                      |
|----------------------|-----------------------------------------------------|
| SchemaAgent          | Structure analysis & data-type compliance           |
| MappingAgent         | Transformation logic generation                     |
| TroubleshootingAgent | Diagnosis of integration execution failures         |
| PerformanceAgent     | Latency & caching optimization recommendations      |
| ConnectorAgent       | Automated connector code generation                 |
| DocumentationAgent   | Automated documentation generation                  |

Responses stream in real time to the React frontend via Server-Sent Events (SSE).

### Enterprise Security & Multi-Tenant Control
- JWT authentication with granular RBAC (Admin, Developer, Auditor)
- Cryptographically hashed tenant API keys with scope restrictions
- Immutable, queryable audit trail for all system and security events

### Caching, Rate Limiting & Observability
- Multi-tier Redis caching (namespace-isolated, sliding expiration, payload compression)
- Sliding-window rate limiter (IP + tenant API-key based)
- Prometheus metrics endpoint + system health diagnostics

---

## System Architecture
┌────────────────────────────────────────────────────────────┐
│           Nginx Reverse Proxy & Load Balancer              │
│     (SSL, HSTS, CSP, Gzip, HTTP 429 Rate Limits)           │
└───────────────────────────┬────────────────────────────────┘
│
┌──────────────────┴──────────────────┐
▼                                     ▼
┌─────────────────────┐             ┌─────────────────────┐
│  React SaaS Frontend│             │  Flask WSGI Gateway │
│ (Vite, Tailwind)    │             │ (Gunicorn, Clean    │
└─────────────────────┘             │  Architecture)      │
└──────────┬──────────┘
│
┌──────────────┬──────────────┬────────────┴────────┬──────────────┐
▼              ▼              ▼                     ▼              ▼
┌─────────┐  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐
│ Multi-  │  │Integration│  │ Multi-Agent  │  │ Monitoring & │  │ Redis    │
│ Tenant  │  │ Engine &  │  │ AI Copilot   │  │ Observability│  │ Cache &  │
│ Client  │  │ Rules     │  │ & RAG        │  │              │  │ Rate     │
│ Service │  │           │  │              │  │              │  │ Limiter  │
└────┬────┘  └────┬─────┘  └──────┬───────┘  └──────┬───────┘  └────┬─────┘
│            │               │                 │               │
└────────────┴───────────────┼─────────────────┴───────────────┘
▼
┌──────────────────────────────┐
│      MySQL 8.0 Relational DB │
│ (Schemas, Audit Logs, State) │
└──────────────────────────────┘
text---

## Technology Stack

| Layer              | Technologies                                              |
|--------------------|-----------------------------------------------------------|
| **Frontend**       | React 18 (JSX), Vite, TailwindCSS, Lucide Icons, Axios    |
| **Backend API**    | Python 3.10, Flask 3.0, Flask-RESTX (Swagger), SQLAlchemy, Gunicorn |
| **Data & Caching** | MySQL 8.0, Redis 7.0 (sliding expiration, compression, tags) |
| **AI & RAG**       | Multi-Agent Orchestrator, Vector Store, BM25, RRF Reranking |
| **DevOps & Infra** | Docker, Docker Compose, Nginx, GitHub Actions CI/CD, Prometheus |

---

## Repository Structure
SyncBridge_AI/
├── backend/
│   ├── app/
│   │   ├── api/v1/               # RESTX Controllers
│   │   ├── ai/                   # Multi-Agent Framework, RAG, Tools & Prompts
│   │   ├── connectors/           # Pluggable Protocol Connectors
│   │   ├── core/                 # Config, Security, Caching, Rate Limiter
│   │   ├── integration_engine/   # Parser, Rules Engine, Transformation Engine
│   │   ├── models/               # SQLAlchemy ORM Models
│   │   ├── repositories/         # Clean Architecture Repositories
│   │   └── services/             # Business Logic Services
│   ├── tests/                    # Pytest suites
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/           # UI Layouts & Modals
│   │   ├── pages/                # Mapping Studio, Playground, Copilot, Monitoring
│   │   └── services/             # Axios API Client
│   └── Dockerfile
├── docker/                       # Nginx configs & Dockerfiles
├── docs/                         # Production DevOps & Deployment Docs
├── scripts/                      # Backup & Disaster Recovery Scripts
├── docker-compose.yml            # Local Development
├── docker-compose.prod.yml       # Production Topology
└── README.md
text---

## Quick Start

### Prerequisites

- Docker v20.10+ and Docker Compose
- (Optional) Python 3.10+ and Node.js 18+ for local development without Docker

### 1. Clone the repository

```bash
git clone https://github.com/Manojkrishna27/Sync_Bridge_Ai.git
cd Sync_Bridge_Ai
2. Configure environment
Bashcp .env.example .env
# Edit .env with your secrets, database credentials, and LLM keys as needed
3. Launch the stack
Development mode
Bashdocker compose -f docker-compose.dev.yml up -d --build
Production mode
Bashdocker compose -f docker-compose.prod.yml up -d --build
4. Access the services

























ServiceURLFrontend Applicationhttp://localhostBackend APIhttp://localhost/api/v1Swagger Docshttp://localhost/api/v1/docsPrometheus Metricshttp://localhost/api/v1/monitoring/prometheus

Running Tests
The repository includes 29 automated test suites covering multi-protocol transformations, AI mapping rules, caching, rate limiting, and RBAC.
BashPYTHONPATH=backend python3 -m pytest backend/tests/ -v
Expected output:
text============================= test session starts ==============================
collected 29 items

backend/tests/test_integration_engine.py ......                        [ 20%]
backend/tests/test_milestone3.py ....                                  [ 34%]
backend/tests/test_milestone5.py .....                                 [ 51%]
backend/tests/test_milestone6.py .....                                 [ 68%]
backend/tests/test_milestone7.py .....                                 [ 86%]
backend/tests/test_milestone8.py ....                                 [100%]======================== 29 passed, 2 warnings in 4.17s ========================
animate-gaussian---

## Disaster Recovery

Automated maintenance scripts live in `scripts/`.

**Create a MySQL backup**
```bash
./scripts/backup.sh
Backups are written to ./backups/mysql_backup_YYYYMMDD_HHMMSS.sql.
Restore from backup
Bash./scripts/restore.sh ./backups/mysql_backup_YYYYMMDD_HHMMSS.sql

API Documentation
Interactive OpenAPI / Swagger documentation is available at:
animate-gaussianhttp://localhost/api/v1/docs
Key endpoint groups:

/api/v1/auth — Authentication & token management
/api/v1/clients — Multi-tenant client management
/api/v1/integrations — Integration definitions & execution
/api/v1/copilot — Multi-agent AI Copilot (SSE)
/api/v1/monitoring — Health & Prometheus metrics


Contributing
Contributions, issues, and feature requests are welcome.

Fork the repository
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add some amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

Please ensure all tests pass and follow the existing code style before submitting.

License
This project is licensed under the MIT License — see the LICENSE file for details.

Built with ❤️ for enterprise integration and AI orchestration.
