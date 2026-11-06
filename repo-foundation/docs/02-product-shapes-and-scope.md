# Product Shapes & Scope Levels

This document establishes standard definitions for **Product Shapes** (the functional topology of the software) and **Scope Levels** (the operational complexity and scale). All numeric thresholds are initial defaults, tune from real use. All cloud pricing references are estimates, verify before use.

> [!IMPORTANT]
> **Permitted vs. Active:** A product shape defines what architectural patterns are **PERMITTED** in the codebase. An architectural capability is only **ACTIVE** when its capability switch evaluates to `true`. All switch triggers, scope derivation rules, and move-up conditions are authoritatively defined in [`docs/05-rules-single-source.md`](05-rules-single-source.md).

---

## 1. Product Shapes

```
[ Demand Test ]  ──────>  [ Small Tool ]  ──────>  [ Multi-User SaaS ]
(Landing / Waitlist)      (Single-purpose CRUD)      (Multi-tenant & Billing)
```

### Shape 1: Demand Test (`demand_test`)
A lightweight web presence designed to validate market interest, capture email leads, or pre-sell a concept before writing core domain logic.

- **Typical Signals:**
  - Validation stage is `idea` or `prototype`.
  - Goal is measuring user interest, signups, or conversion intent.
  - No persistent user accounts or multi-step computational workflows required.
- **What is Permitted (Baseline):**
  - Single-page or multi-section responsive landing page.
  - Simple lead capture or waitlist form with CSRF protection and honeypot spam prevention.
  - Submission storage (lightweight SQLite records or simple email notification forwarder).
  - Clear confirmation screen or thank-you page.
- **What is Explicitly Excluded:**
  - User login, passwords, session state management, or account profile dashboards.
  - Payment gateway checkouts, subscriptions, or credit card handling.
  - Multi-tenant data segregation.
  - Background worker daemons or task brokers.
- **When to Move Up:**
  - For the authoritative rules governing transitions between product shapes, see [`docs/05-rules-single-source.md`](05-rules-single-source.md#4-rules-for-when-a-project-moves-up).

---

### Shape 2: Small Tool (`small_tool`)
A focused, single-purpose application built to solve a specific operational task for an individual, a single company team, or a narrow group of users.

- **Typical Signals:**
  - 0 to 499 active users; often internal or single-tenant.
  - Clear, straightforward data flow: user inputs data, system processes or stores it, user views or downloads results.
  - No need to isolate multiple competing client organizations from each other.
- **What is Permitted (Baseline):**
  - Simple user authentication (e.g., standard Django session auth or built-in Django admin).
  - Single database schema with relational models.
  - Core domain CRUD (Create, Read, Update, Delete) forms, views, and dashboards.
  - Standard synchronous processing for business logic.
  - Basic unit and regression test coverage for domain rules.
- **What is Explicitly Excluded:**
  - Complex multi-tenant isolation schemas (tenants sharing a single DB with strict organization filters).
  - Multi-tier subscription billing with credit balances and metered usage.
  - Real-time WebSockets or microservice splits.
  - Distributed message brokers and asynchronous worker pools.
- **When to Move Up:**
  - For the authoritative rules governing transitions between product shapes, see [`docs/05-rules-single-source.md`](05-rules-single-source.md#4-rules-for-when-a-project-moves-up).

---

### Shape 3: Multi-User SaaS (`multi_user_saas`)
A commercial software-as-a-service application serving multiple independent users or organizations, often monetized via subscriptions or usage fees.

- **Typical Signals:**
  - Multiple unrelated accounts or organizations sharing the application.
  - Requires subscription billing, account registration, self-service password resets, and team invite flows.
  - Third-party webhooks (e.g., payment confirmations, transactional emails).
- **What is Permitted (Active only when corresponding capability switch is ON):**
  - Organization/tenant data scoping to strictly prevent cross-account data leaks.
  - User authentication suite: registration, email verification, password reset, and role flags (Admin vs Member).
  - Payment processor integration (e.g., hosted checkout sessions and webhook event verification).
  - Asynchronous background task execution for webhooks and emails *(active only when `background_jobs` switch is ON per docs/05)*.
  - Rate limiting on public and authenticated endpoints *(active only when `rate_limiting` switch is ON per docs/05)*.
  - Managed PostgreSQL database server *(active only when `postgres` switch is ON per docs/05; otherwise runs on SQLite in small scope)*.
- **What is Explicitly Excluded:**
  - Custom enterprise SAML/SSO federation (unless classified under Enterprise scope).
  - Multi-region database sharding.
  - Unnecessary microservices architecture (maintains a modular monolith).
- **When to Move Up:**
  - For the authoritative rules governing transitions between product shapes, see [`docs/05-rules-single-source.md`](05-rules-single-source.md#4-rules-for-when-a-project-moves-up).

---

## 2. Scope Levels

The intake conversation never asks a user for `scope_level` directly; it is deterministically derived from `expected_users`, `data_sensitivity`, and `validation_stage` as defined in [`docs/05-rules-single-source.md`](05-rules-single-source.md#1-scope-level-derivation--the-highest-signal-wins-rule). Note that `team_size` is decoupled from scope derivation and directly drives only `ci` and `docker`.

Scope boundaries use strict, non-overlapping user count ranges (initial defaults, tune from real use):

| Scope Level | User Count (`expected_users`) | Operational Footprint | Status |
| :--- | :--- | :--- | :--- |
| **Small** (`small`) | 0 – 499 users | Single process, SQLite, local/persistent storage, synchronous | Implemented |
| **Medium** (`medium`) | 500 – 9,999 users | Managed Postgres, Redis, background workers (evidence-based), CI pipeline | Implemented |
| **Enterprise** (`enterprise`) | 10,000+ users | High-availability PostgreSQL, SAML/SSO, audit logs, HA replicas | **Defined, Not Yet Implemented** |

*(Note: Team size is decoupled from scope derivation; team size >= 2 directly triggers CI and Docker tooling, but does not alter scope level).*

---

### Scope Level 1: Small (`small`)
- **Typical Signals:**
  - Pre-seed, bootstrapped, or internal projects.
  - 0 to 499 expected users.
  - Low concurrency (<5 concurrent requests/second).
  - Monthly infrastructure budget: $0 to under $50 (`zero` or `bootstrap`, verify before use).
- **What is Included (Typically active only when the capability switch is ON):**
  - Single-process web server deployment (e.g., WSGI/Gunicorn on basic VPS or PaaS).
  - Embedded SQLite database (zero configuration, no separate database server process).
  - Local disk storage for static and uploaded files (or persistent container volume if deployed on PaaS).
  - Synchronous request handling.
  - Local test commands (`python manage.py test`).
- **What is Explicitly Excluded:**
  - Docker containerization orchestration (runs directly in standard Python virtual environment, unless `team_size >= 2`).
  - Redis caches and Celery worker daemons (unless triggered by `escalation_signals`).
  - Continuous Integration (CI) multi-stage build pipelines (unless `team_size >= 2`).
  - External paid error-monitoring services.
- **When to Move Up to Medium:**
  - For the authoritative rules governing when a project moves up from Small to Medium, see [`docs/05-rules-single-source.md`](05-rules-single-source.md#4-rules-for-when-a-project-moves-up).

---

### Scope Level 2: Medium (`medium`)
- **Typical Signals:**
  - Revenue-generating or mission-critical tool.
  - 500 to 9,999 active users.
  - Monthly infrastructure budget: $50 to $500 (`growth`, verify before use).
- **What is Included (Typically active only when the capability switch is ON):**
  - Managed PostgreSQL database server with connection pooling and automated daily snapshots.
  - Dockerfile and `docker-compose.yml` for identical local and staging environments (when `team_size >= 2`).
  - Automated CI test runner (e.g., GitHub Actions) executing unit and integration tests on pull requests (when `team_size >= 2`).
  - Centralized error telemetry (e.g., Sentry baseline integration, verify before use).
  - Automated rate limiting and database backup routines.
  - Asynchronous background task queue powered by Redis (evidence-based: active only when `slow_sync_calls` signal is present).
- **What is Explicitly Excluded:**
  - Kubernetes cluster management or distributed microservices.
  - Multi-region database replication.
  - Custom hardware security modules or customer-managed encryption keys.
- **When to Move Up to Enterprise:**
  - For the authoritative rules governing when a project moves up from Medium to Enterprise, see [`docs/05-rules-single-source.md`](05-rules-single-source.md#4-rules-for-when-a-project-moves-up).

---

### Scope Level 3: Enterprise (`enterprise`)
> **Status: Defined, Not Yet Implemented**
> This scope level is formally specified for architectural completeness, but code scaffolding and automated recipes are not yet active in this repository version. See [`docs/05-rules-single-source.md` Section 1.3](05-rules-single-source.md#13-behavior-when-derived-scope-is-enterprise-not-implemented) for LLM handling behavior when this tier is derived.

- **Typical Signals:**
  - 10,000+ active users or contracts with enterprise procurement departments.
  - High availability requirement (99.99% uptime SLA).
  - Legal compliance requirements: HIPAA, SOC2 Type II, ISO 27001, or PCI-DSS Level 1.
- **What is Included (Specification):**
  - Enterprise Single Sign-On (SAML 2.0 / Okta / Azure AD).
  - Granular Attribute-Based Access Control (ABAC) and immutable audit log streams.
  - High-availability database clusters with multi-AZ automatic failover and read replicas.
  - Automated static analysis, secret scanning, and container vulnerability scanning in CI/CD.
  - Formal compliance control checklists and baseline evidence collection.
- **What is Explicitly Excluded:**
  - Unnecessary architectural re-platforming (monolithic codebases remain monolithic unless domain boundaries mandate microservices).
- **When to Move Up:**
  - Not applicable (highest defined tier). See [`docs/05-rules-single-source.md`](05-rules-single-source.md#4-rules-for-when-a-project-moves-up) for boundary definitions.
