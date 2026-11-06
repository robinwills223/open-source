# Project Profile Specification

The `project.profile.yaml` file is the central source of truth for any project initialized through this repository. Generated during the initial conversational intake, this file documents the project's audience, functional shape, operational constraints, capability switches, and any developer overrides.

No code scaffolding or architectural recommendations should occur before this file is generated and validated. All numeric thresholds are initial defaults, tune from real use.

---

## 1. Schema Overview

The profile is validated against the formal JSON Schema located at [`schemas/project.profile.schema.json`](../schemas/project.profile.schema.json).

### Example File Structure (`project.profile.yaml`)
```yaml
profile_version: 1
name: invoice-parser
description: "A simple internal tool that extracts line items from PDF invoices into CSV."
audience: non_technical_founder
product_shape: small_tool
scope_level: small
stack: django
expected_users: 5
team_size: 1
data_sensitivity: none
budget_range: bootstrap
validation_stage: prototype
founder_region: US
hosting_target: vps
escalation_signals: []
capabilities:
  docker: false
  postgres: false
  redis: false
  background_jobs: false
  ci: false
  error_monitoring: false
  compliance_checklist: false
  rate_limiting: false
  minimum_viable_backup: false
  backups: false
```

---

## 2. Plain-Language Field Definitions

Below is a plain-language explanation of each field required in the project profile:

### `profile_version` *(integer, required)*
- **What it means:** The schema version of this profile document (starts at `1`).
- **Why it matters:** Ensures forward-compatibility as the repository evolutions introduce new schema features.

### `name` *(string, required)*
- **What it means:** A short, unique identifier for your project.
- **Rules:** Use only lowercase letters, numbers, and hyphens (e.g., `client-billing-tool`).
- **Why it matters:** Used for folder names, database identifiers, and local configuration files.

### `description` *(string, optional but recommended)*
- **What it means:** A simple summary of what the product does in everyday words.
- **Why it matters:** Keeps the LLM focused on your actual product goals rather than generic software patterns.

### `audience` *(string, required)*
- **Allowed values:**
  - `non_technical_founder`: Focuses on business results, non-technical explanations, and automatic safe defaults. Overrides are disabled.
  - `junior_developer`: Focuses on clean architecture, code explanations, and learning standard conventions. Overrides allowed with recorded warnings.
  - `senior_developer`: High-density technical communication, code diffs, and immediate configuration overrides.
- **Why it matters:** Directs the LLM to speak in the right tone, ask the right number of questions, and provide appropriate guardrails.

### `product_shape` *(string, required)*
- **Allowed values:**
  - `demand_test`: A landing page or waitlist form to check customer interest before building features.
  - `small_tool`: A focused utility for one team or a narrow group of users (e.g., internal dashboard, calculator).
  - `multi_user_saas`: A full service where different customers register accounts, pay, and manage their own data.
- **Why it matters:** Prevents building user accounts or billing systems when all you need is a landing page or internal utility. Also directly triggers `rate_limiting` when set to `multi_user_saas`.

### `scope_level` *(string, required)*
- **Allowed values:** `small`, `medium`, `enterprise`
- **Derivation Notice:** The intake conversation **never** asks the user for this field directly. It is computed deterministically from `expected_users`, `data_sensitivity`, and `validation_stage` using the highest-signal-wins rule defined in [`docs/05-rules-single-source.md#1-scope-level-derivation--the-highest-signal-wins-rule`](05-rules-single-source.md#1-scope-level-derivation--the-highest-signal-wins-rule). Note that `team_size` is decoupled and does not alter `scope_level`.
- **Scope Boundaries:** Non-overlapping boundaries for each level (Small: 0–499 users; Medium: 500–9,999 users; Enterprise: 10,000+ users) are authoritatively defined in [`docs/05-rules-single-source.md#3-non-overlapping-scope-boundaries`](05-rules-single-source.md#3-non-overlapping-scope-boundaries). All thresholds are initial defaults, tune from real use.
- **Why it matters:** Sets the foundational operational footprint and baseline infrastructure requirements.

### `stack` *(string, required)*
- **Allowed values:** `django`
- **Why it matters:** Specifies the base framework. In this initial release, Django is the sole supported stack because of its robust built-in security, standard ORM, and integrated admin portal.

### `expected_users` *(integer, required)*
- **What it means:** Estimated count of monthly active users or customer accounts anticipated over the next 3 to 6 months.
- **Why it matters:** Directly drives the user threshold for `scope_level` and `rate_limiting`.

### `team_size` *(integer, required)*
- **What it means:** How many developers will write and merge code into this repository.
- **Why it matters:** Decoupled from `scope_level`. Directly drives `ci` and `docker` capability triggers when `team_size >= 2`.

### `data_sensitivity` *(string, required)*
- **Allowed values:**
  - `none`: Public or non-confidential information (e.g., public directory, landing page metrics).
  - `personal`: Basic user profiles, email addresses, names, and passwords.
  - `payments_hosted`: Customer checkout handled via external hosted redirect (e.g., Stripe Checkout, LemonSqueezy) where card numbers never touch the application server.
  - `payments_direct`: Direct transmission or storage of credit card numbers on your application server. *(Strongly discouraged for all audiences; triggers heavy compliance requirements).*
  - `health`: Patient information, medical records, or sensitive health data.
- **Why it matters:** Directly drives compliance checks and scope derivation.

### `budget_range` *(string, required)*
- **Allowed values:**
  - `zero`: $0/month. Operates strictly on free tiers or local machines.
  - `bootstrap`: Under $50/month. Single low-cost virtual private server or PaaS starter plan.
  - `growth`: $50 to $500/month. Managed databases, background workers, and automated backup services.
  - `high`: Over $500/month. High availability, multi-region clustering, and formal compliance monitoring.
- **Conflict Guidance:** If a derived `scope_level` requires infrastructure exceeding the budget, the LLM provides an explicit plain-language warning and recommends low-cost alternatives without altering architecture without recorded explanation in `DECISIONS-FOR-FOUNDER.md`. See [`docs/05-rules-single-source.md#12-budget-conflict-detection--guidance`](05-rules-single-source.md#12-budget-conflict-detection--guidance).
- **Why it matters:** Prevents recommending paid cloud services that exceed your financial comfort zone.

### `validation_stage` *(string, required)*
- **Allowed values:**
  - `idea`: Concept phase; no code or users yet.
  - `prototype`: Building an initial working demonstration to test functionality.
  - `validated_pre_revenue`: Active non-paying test users providing feedback.
  - `paying_customers`: Live product with real commercial transactions.
  - `scaling`: Expanding capacity, team size, and market reach.
- **Why it matters:** Directly asked during intake. Stages from `validated_pre_revenue` onward strictly require `minimum_viable_backup: true`.

### `founder_region` *(string, optional)*
- **Allowed values:** Two-letter ISO country code (e.g., `US`, `GB`, `CA`) or `EU`.
- **Why it matters:** Ensures the LLM verifies payment provider availability, sales tax/VAT remittance, and data protection rules before recommending third-party services (verify before use).

### `hosting_target` *(string, required)*
- **Allowed values:** `local`, `vps`, `paas_ephemeral`, `paas_persistent`, `managed`
- **Why it matters:** Target deployment hosting environment. Inferred deterministically during intake per [`docs/05-rules-single-source.md` Section 7](05-rules-single-source.md#7-deterministic-hosting-target-inference) and recorded in `DECISIONS-FOR-FOUNDER.md`.
- **Enforcement Rule:** Setting `hosting_target: paas_ephemeral` while using SQLite (`postgres: false`) is strictly invalid in the schema.

### `escalation_signals` *(array of strings, optional)*
- **Allowed values:** Subset of `["sqlite_lock_contention", "slow_sync_calls", "high_traffic_bursts"]`.
- **Why it matters:** Operational telemetry signals from real use that trigger targeted capability upgrades:
  - `slow_sync_calls` requires `background_jobs: true` and `redis: true`.
  - `sqlite_lock_contention` requires `postgres: true`.
  - `high_traffic_bursts` requires `redis: true` and `rate_limiting: true`.

### `overrides` *(array of objects, optional)*
- **Format:** List of `{capability, value, reason}` (reason minLength 10).
- **Rules:** Allowed only for `junior_developer` (with recorded warning in `DECISIONS-FOR-FOUNDER.md`) or `senior_developer`. Prohibited for `non_technical_founder`. Inviolable safety floors (MVB, compliance, ephemeral PaaS safeguards) cannot be overridden.

### `capabilities` *(object, required)*
- **What it means:** A map containing all ten required boolean flags (`docker`, `postgres`, `redis`, `background_jobs`, `ci`, `error_monitoring`, `compliance_checklist`, `rate_limiting`, `minimum_viable_backup`, `backups`).
- **Enforced Schema Rules:**
  - If `validation_stage` is in `[validated_pre_revenue, paying_customers, scaling]`, `minimum_viable_backup` MUST be `true`.
  - If `data_sensitivity` is in `[payments_direct, health]`, `compliance_checklist` MUST be `true`.
  - If `hosting_target` is `paas_ephemeral`, `postgres` MUST be `true`.
  - If `slow_sync_calls` is in `escalation_signals`, `background_jobs` and `redis` MUST be `true`.
  - If `sqlite_lock_contention` is in `escalation_signals`, `postgres` MUST be `true`.
  - If `high_traffic_bursts` is in `escalation_signals`, `redis` MUST be `true`.
- **Why it matters:** Evaluated authoritatively via [`docs/05-rules-single-source.md#6-authoritative-capability-trigger-matrix`](05-rules-single-source.md#6-authoritative-capability-trigger-matrix).
