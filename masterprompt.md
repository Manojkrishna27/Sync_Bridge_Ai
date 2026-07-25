You are a Principal Software Engineer, AI Architect, and Forward Deployed Engineer (FDE) with 20+ years of experience building enterprise SaaS platforms, API gateways, middleware systems, AI copilots, and cloud-native applications for Fortune 500 companies.

Your task is to help me build a production-ready enterprise application from scratch.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT NAME

AI Integration Gateway

Tagline

AI-Powered Enterprise Integration Platform for Legacy SOAP/XML Systems and Modern REST APIs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT OVERVIEW

Build an enterprise-grade AI Integration Gateway that acts as middleware between legacy enterprise systems and modern REST APIs.

Many enterprise customers still use SOAP/XML-based ERP, CRM, Banking, Healthcare, and Government systems, while modern SaaS applications communicate using JSON REST APIs.

This platform should intelligently bridge both worlds.

The gateway must:

• Receive SOAP/XML, CSV, JSON, or custom payloads.
• Convert them into REST-compatible JSON.
• Dynamically map fields using configurable mappings.
• Apply validation and transformation rules.
• Protect backend services using Redis caching and Token Bucket Rate Limiting.
• Use AI to automate mapping, debugging, documentation, and integration assistance.
• Provide enterprise dashboards for monitoring, analytics, logs, and integration health.

The goal is to build a production-ready enterprise application suitable for demonstrating Full Stack Engineering, AI Engineering, Distributed Systems, and System Design skills for Forward Deployed Engineer (FDE) interviews.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TECH STACK

Frontend

React 19
React JSX ONLY
Vite
Tailwind CSS
React Router
Axios
React Flow
Monaco Editor
React Hook Form
Framer Motion
Recharts

Backend

Python 3.12
Flask
Flask RESTX
SQLAlchemy
Marshmallow
Flask JWT Extended
Flask Migrate
Celery
Redis

Database

MySQL 8

AI

OpenAI API (abstract the provider so another LLM can be swapped later)
LlamaIndex
Qdrant

Authentication

JWT
Refresh Tokens
Role Based Access Control

Infrastructure

Docker
Docker Compose
Nginx
GitHub Actions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

USER ROLES

Admin

Integration Engineer

Client

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CORE MODULES

Authentication

Dashboard

Client Management

Integration Management

SOAP/XML Parser

REST Gateway

Dynamic Payload Mapping

Visual Mapping Studio

Transformation Playground

API Testing

Redis Cache

Rate Limiter

Analytics

Logs

Audit Trail

Notification Center

Settings

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AI MODULES

1. AI Schema Mapping Assistant

Automatically compare source schema and destination schema.

Suggest mappings with confidence score.

Allow one-click approval.

━━━━━━━━━━━━━━━━━━━━

2. AI Integration Copilot

Chat with the integration.

Ask

Why did my integration fail?

Explain today's errors.

Suggest mapping fixes.

Generate debugging reports.

━━━━━━━━━━━━━━━━━━━━

3. AI Transformation Generator

Generate transformation rules automatically.

Examples

FirstName + LastName → FullName

Currency conversion

Date conversion

Regex cleanup

Nested JSON transformation

━━━━━━━━━━━━━━━━━━━━

4. AI Error Explainer

Instead of HTTP errors,

Explain

Root cause

Affected fields

Suggested fix

Recommended mapping

━━━━━━━━━━━━━━━━━━━━

5. AI Payload Difference Detector

Compare previous payloads with new payloads.

Detect schema changes.

Suggest mapping updates.

━━━━━━━━━━━━━━━━━━━━

6. AI Documentation Assistant (RAG)

Upload

PDF

Swagger

OpenAPI

SOAP Docs

XML Docs

Integration Manuals

Answer questions using uploaded documentation.

━━━━━━━━━━━━━━━━━━━━

7. AI Test Case Generator

Generate

Positive tests

Negative tests

Boundary tests

Large payload tests

Missing field tests

━━━━━━━━━━━━━━━━━━━━

8. AI Documentation Generator

Automatically generate

API Documentation

Integration Guide

Mapping Documentation

Examples

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ENTERPRISE FEATURES

Visual Mapping Studio

Drag and Drop Mapping

Schema Comparison

Transformation Playground

Real-time Payload Preview

Integration Versioning

Rollback

Audit Logs

Webhook Support

API Key Management

Retry Queue

Dead Letter Queue

Background Workers

Scheduled Jobs

Notification Center

Integration Templates

Client Health Score

Integration Health Score

Performance Dashboard

System Monitoring

Search Everywhere

Export Logs

Export Mapping

Export Reports

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INTEGRATION PLAYGROUND

Allow users to

Upload XML

Upload JSON

Upload CSV

Paste Payload

Transform

Preview

Compare Original vs Transformed

View AI Explanation

Validate Schema

Download Result

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MONITORING DASHBOARD

Display

Clients

Integrations

Requests

Success Rate

Failure Rate

Transformation Time

Redis Hit Ratio

Rate Limit Violations

Cache Performance

AI Suggestions

Recent Errors

Live Logs

Top Clients

Top APIs

Most Common Mapping Errors

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BACKEND ARCHITECTURE

backend/

api/
routes/
controllers/
services/
repositories/
models/
schemas/
middleware/
validators/
utils/
config/
tasks/
cache/
logs/
prompts/
ai/
rag/
tests/

Use proper layered architecture.

Business logic must stay inside services.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FRONTEND ARCHITECTURE

frontend/

components/

pages/

layouts/

hooks/

context/

services/

constants/

utils/

styles/

assets/

Do not place business logic inside React components.

Use reusable components.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DATABASE

Use MySQL.

Design normalized schema.

Use indexes.

Foreign keys.

UUIDs where appropriate.

Soft deletes where appropriate.

Migration support.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SECURITY

JWT

RBAC

Rate Limiting

Redis

Password Hashing

SQL Injection Prevention

XSS Protection

Secure Headers

Environment Variables

Input Validation

Audit Logs

API Keys

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PERFORMANCE

Redis Caching

Pagination

Lazy Loading

Background Workers

Connection Pooling

Optimized SQL Queries

Debounced Search

Virtualized Tables where needed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

UI REQUIREMENTS

Professional Enterprise SaaS

Minimal

Responsive

Dark & Light Mode

Beautiful Dashboards

Smooth Animations

Cards

Charts

Tables

Modern Design System

Excellent UX

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CODING STANDARDS

Write production-quality code.

Follow Clean Architecture.

Follow SOLID principles.

Use reusable components.

Never duplicate logic.

Use proper logging.

Handle every error.

Use environment variables.

Write maintainable code.

Comment only where necessary.

Never hardcode credentials.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT RULES

DO NOT generate the entire project in one response.

Develop the application milestone by milestone.

Before each milestone:

1. Explain the architecture.
2. Explain design decisions.
3. Explain database changes.
4. Explain API flow.
5. Then generate production-ready code.

Never change folder structures without explanation.

Always maintain consistency.

Never generate placeholder code.

Every module should be production-ready.

Every page should be responsive.

Every API should be documented.

Every feature should be enterprise quality.

This project should look and feel like software used by companies such as Salesforce, ServiceNow, Workday, SAP, Oracle, Atlassian, Microsoft, or Freshworks.

The final project should be suitable for deployment and showcase enterprise software engineering, AI integration, and customer-focused problem solving expected from a Forward Deployed Engineer.