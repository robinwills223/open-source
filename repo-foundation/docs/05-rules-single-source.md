# Single Source of Truth: Rules, Derivations & Triggers

This document is the **sole authoritative source** for:
1. How `scope_level` is derived from intake inputs.
2. The boundaries defining each scope level and product shape.
3. The rules for when a project moves up a scope level.
4. The exact trigger conditions that turn capability switches ON or OFF.
5. Deterministic inference and safeguards for `hosting_target`.
6. Minimum viable backup (MVB) requirements and ephemeral SQLite safeguards.
7. Operational escalation signals (`escalation_signals`).
8. Developer override protocols and non-overridable safety floors.
9. Regional verification requirements for payments, taxes, and data privacy.
10. Budget conflict detection and guidance.

No other document defines these rules. All other documents link here. All numeric thresholds stated herein are **initial defaults, tune from real use**. All third-party provider claims and pricing references are marked **verify before use**.

---

## 1. Scope Level Derivation & The Highest-Signal-Wins Rule

The intake conversation **never** asks a user to select a `scope_level` directly. Instead, `scope_level` is deterministically computed from three observable project profile inputs:
- `expected_users`
- `data_sensitivity`
- `validation_stage`

> [!IMPORTANT]
> **Decoupling `team_size`:** `team_size` is **not** an input to `scope_level` derivation. A team of two building a prototype with 20 users remains in `small` scope. `team_size` directly drives **only** the `ci` and `docker` capability triggers.

### 1.1 Input Tier Mapping Matrix

*(All numeric thresholds are initial defaults, tune from real use.)*

| Input Field | Small Tier (`small`) | Medium Tier (`medium`) | Enterprise Tier (`enterprise`) |
| :--- | :--- | :--- | :--- |
| **`expected_users`** | 0 to 499 | 500 to 9,999 | 10,000+ |
| **`data_sensitivity`** | `none`, `personal`, `payments_hosted` | `payments_direct` | `health` |
| **`validation_stage`** | `idea`, `prototype`, `validated_pre_revenue`, `paying_customers` | `scaling` | — |

> [!NOTE]
> - `payments_hosted`: Customer payments are processed using external hosted checkout or redirect sessions (e.g. Stripe Checkout, LemonSqueezy). Credit card numbers **never touch** the application server. This maps to **Small** when user count is under 500.
> - `payments_direct`: Credit card numbers are transmitted or processed directly on the application server. This maps to **Medium** and triggers strict baseline compliance audits. Direct card handling is **strongly discouraged** for all audiences in this repository.

### 1.2 The Highest-Signal-Wins Rule
`scope_level` equals the highest tier triggered across any of the three inputs:

$$\text{scope\_level} = \max(\text{tier}(\text{expected\_users}), \text{tier}(\text{data\_sensitivity}), \text{tier}(\text{validation\_stage}))$$

Ordered by precedence:
$$\text{small} < \text{medium} < \text{enterprise}$$

### 1.3 Behavior When Derived Scope is "enterprise" (Not Implemented)
If `scope_level` derives to `enterprise` (e.g., due to `expected_users >= 10,000` or `data_sensitivity: health`):
1. The LLM must state plainly to the user:
   > *"The Enterprise scope level is formally defined in our architecture specifications, but automated code scaffolding and operational recipes for enterprise requirements (e.g. SAML SSO, HIPAA BAA compliance, multi-region failover) are not yet implemented in this repository."*
2. The LLM explains why enterprise support cannot be safely scaffolded by a generic generator.
3. The LLM offers a scoped-down non-sensitive prototype (e.g., handling non-sensitive or mock data under `small` or `medium` scope) for initial workflow validation.
4. The LLM **must not proceed to scaffold** application code or infrastructure for an enterprise-scoped profile.

---

## 2. Worked Examples for Scope Derivation

### Worked Example A: Deriving Small Scope
- **Inputs:** `expected_users: 15`, `team_size: 1`, `data_sensitivity: none`, `validation_stage: prototype`.
- **Field Evaluations:**
  - `expected_users: 15` &rarr; `small` (0–499)
  - `data_sensitivity: none` &rarr; `small`
  - `validation_stage: prototype` &rarr; `small`
- **Result:** $\max(\text{small}, \text{small}, \text{small}) =$ **`small`**.

### Worked Example B: Small Scope with Multiple Contributors (Decoupled `team_size`)
- **Inputs:** `expected_users: 100`, `team_size: 2`, `data_sensitivity: personal`, `validation_stage: paying_customers`.
- **Field Evaluations:**
  - `expected_users: 100` &rarr; `small`
  - `data_sensitivity: personal` &rarr; `small`
  - `validation_stage: paying_customers` &rarr; `small`
- **Result:** $\max(\text{small}, \text{small}, \text{small}) =$ **`small`**.
- **Capability Effect:** `scope_level` remains `small`. However, `team_size: 2` directly triggers `ci: true` and `docker: true`.

### Worked Example C: Deriving Medium Scope
- **Inputs:** `expected_users: 2500`, `team_size: 3`, `data_sensitivity: payments_hosted`, `validation_stage: paying_customers`.
- **Field Evaluations:**
  - `expected_users: 2500` &rarr; `medium` (500–9,999)
  - `data_sensitivity: payments_hosted` &rarr; `small`
  - `validation_stage: paying_customers` &rarr; `small`
- **Result:** $\max(\text{medium}, \text{small}, \text{small}) =$ **`medium`**.

### Worked Example D: Deriving Enterprise Scope (Blocked)
- **Inputs:** `expected_users: 50`, `team_size: 1`, `data_sensitivity: health`, `validation_stage: prototype`.
- **Field Evaluations:**
  - `expected_users: 50` &rarr; `small`
  - `data_sensitivity: health` &rarr; `enterprise`
  - `validation_stage: prototype` &rarr; `small`
- **Result:** $\max(\text{small}, \text{enterprise}, \text{small}) =$ **`enterprise`**.
- **Action:** LLM halts scaffolding per Section 1.3 and offers non-sensitive prototype.

---

## 3. Non-Overlapping Scope Boundaries

*(All numeric thresholds are initial defaults, tune from real use.)*

| Scope Level | User Count (`expected_users`) | Typical Team Size | Database Default | Runtime Architecture |
| :--- | :--- | :--- | :--- | :--- |
| **`small`** | 0 to 499 | 1 to 2 builders (note: team size is decoupled) | Embedded SQLite | Single process, synchronous execution |
| **`medium`** | 500 to 9,999 | 2 to 5 builders (note: team size is decoupled) | Managed PostgreSQL | Dockerized, Redis broker, background workers |
| **`enterprise`** | 10,000+ | 6+ builders (note: team size is decoupled) | High-Availability PostgreSQL | Multi-AZ, SAML SSO, audit streams *(Spec only)* |

---

## 4. Rules for When a Project Moves Up

A project moves up from its current scope level to a higher level **if and only if** at least one of the following events occurs:

### Moving from `small` to `medium`:
1. **User Growth:** `expected_users` reaches or exceeds **500**.
2. **Data Elevation:** `data_sensitivity` changes to **`payments_direct`** (or **`health`**).
3. **Validation Progression:** `validation_stage` transitions to **`scaling`**.
4. **Operational Pressure:** Observed `escalation_signals` (such as `sqlite_lock_contention` or `slow_sync_calls`).

### Moving from `medium` to `enterprise`:
1. **Enterprise Scale:** `expected_users` reaches or exceeds **10,000**.
2. **Regulated Health Data:** `data_sensitivity` becomes **`health`**.
3. **Institutional Mandates:** External commercial contracts require formal SOC2 Type II compliance, HIPAA BAA, SAML 2.0 / Okta SSO, or immutable audit logging.

---

## 5. Permitted vs. Active Capabilities

A strict architectural distinction exists between **product shape** and **capability switches**:
- **Product Shape defines what is PERMITTED:** It sets architectural boundaries and patterns that are allowable within the codebase.
- **Capability Switches define what is ACTIVE:** A capability is compiled into settings and runtime dependencies **only** when its specific switch evaluates to `true`.

---

## 6. Authoritative Capability Trigger Matrix

Triggers alone decide capability states. Heavy infrastructure components (worker queues, in-memory caches) are strictly evidence-based and respond to measured production problems rather than user counts.

Every capability is **OFF (`false`)** unless its exact trigger condition evaluates to `true`:

| Capability | Default | Exact Trigger Condition | Plain-Language Rationale |
| :--- | :--- | :--- | :--- |
| **`docker`** | `false` | `team_size >= 2` | Container tooling overhead is unnecessary for solo builders on local Python, but required for multi-developer consistency. |
| **`postgres`** | `false` | `scope_level in ["medium", "enterprise"]` OR `"sqlite_lock_contention" in escalation_signals` | SQLite handles zero-config single-node reads/writes until medium concurrency scale or measured lock contention requires PostgreSQL. |
| **`redis`** | `false` | `background_jobs == true` OR `"high_traffic_bursts" in escalation_signals` | In-memory key-value stores add hosting expense and failure points; enabled only when backing an active job queue or absorbing traffic bursts. |
| **`background_jobs`** | `false` | `"slow_sync_calls" in escalation_signals` | Worker queues answer measured slow synchronous calls (HTTP timeouts >3s), not hypothetical future tasks. |
| **`ci`** | `false` | `team_size >= 2` | Automated pull-request pipelines add maintenance overhead before multiple developers merge code. |
| **`error_monitoring`** | `false` | `scope_level in ["medium", "enterprise"]` | Centralized telemetry SaaS (e.g. Sentry, verify before use) requires API keys and network egress. |
| **`compliance_checklist`** | `false` | `data_sensitivity in ["payments_direct", "health"]` OR `scope_level == "enterprise"` | Heavy regulatory audits apply only when handling raw cardholder data or health records. Hosted checkout does NOT trigger this. |
| **`rate_limiting`** | `false` | `expected_users >= 500` OR `scope_level in ["medium", "enterprise"]` OR `product_shape == "multi_user_saas"` OR `"high_traffic_bursts" in escalation_signals` | Throttling protects public endpoints and multi-user SaaS environments against abuse. |
| **`minimum_viable_backup`** | `false` | `validation_stage in ["validated_pre_revenue", "paying_customers", "scaling"]` | Protects real user data as soon as beta users arrive, independent of scope level. |
| **`backups`** | `false` | `scope_level in ["medium", "enterprise"]` | Automated cloud-managed database snapshots with retention policies require cloud infrastructure services. |

> [!NOTE]
> **Supersession:** When both `backups` and `minimum_viable_backup` evaluate to `true`, the full automated snapshot suite (`backups`) **supersedes** MVB in runtime infrastructure, while the documented manual restore drill from MVB is retained.

---

## 7. Deterministic Hosting Target Inference

`hosting_target` is a required profile field (`local`, `vps`, `paas_ephemeral`, `paas_persistent`, `managed`). During intake, the LLM infers `hosting_target` deterministically without asking, and records the selection in `DECISIONS-FOR-FOUNDER.md`:

### 7.1 Inference Matrix

| Product Shape | Validation Stage | Budget Range | Inferred `hosting_target` | Plain-Language Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **`demand_test`** | Any | `zero` | `paas_persistent` | Public waitlist cannot run locally. Requires reachable host (e.g. Fly.io free volume, verify before use) with recorded advisory. |
| **`demand_test`** | Any | `bootstrap` / `growth` / `high` | `paas_persistent` | Public waitlist hosted on low-cost persistent PaaS. |
| **`small_tool`** / **`multi_user_saas`** | `idea` / `prototype` | `zero` | `local` | Prototyping on developer's local machine incurs $0 cost. |
| **`small_tool`** / **`multi_user_saas`** | `idea` / `prototype` | `bootstrap` | `local` | Safe local default; founder can confirm `vps` / `paas_persistent` if sharing a live demo. |
| **`small_tool`** / **`multi_user_saas`** | `idea` / `prototype` | `growth` / `high` | `managed` | Funded prototype deploying directly to managed cloud. |
| **`small_tool`** / **`multi_user_saas`** | `validated_pre_revenue`+ | `zero` | `paas_persistent` | **Core Principle:** A product with real beta or paying users cannot be served reliably from a local laptop. Emits budget advisory and defaults to persistent PaaS recommendation. |
| **`small_tool`** / **`multi_user_saas`** | `validated_pre_revenue`+ | `bootstrap` | `paas_persistent` | Persistent container disk provides low-cost single-node stability. |
| **`small_tool`** / **`multi_user_saas`** | `validated_pre_revenue`+ | `growth` / `high` | `managed` | Production workload with budget for managed PostgreSQL/container hosting. |

### 7.2 Ephemeral PaaS Invalidation Rule
`hosting_target == "paas_ephemeral"` with `capabilities.postgres == false` is **strictly INVALID** in the schema.
Many PaaS containers wipe disk state on redeploy or restart. An embedded SQLite file stored in an ephemeral container will be **permanently erased**.
The confirmed resolution must either:
1. Change `hosting_target` to `paas_persistent` (volume attached).
2. Set `postgres: true` (managed database attached).

---

## 8. Minimum Viable Backup (MVB) Requirements

- **Active When:** `validation_stage in ["validated_pre_revenue", "paying_customers", "scaling"]`.
- **Baseline Requirements:**
  1. **SQLite Native Backup Command:** Backups of SQLite databases **must use SQLite's native backup API (`.backup` command or `VACUUM INTO 'backup.db'`)**, never a raw file copy of an actively open, live database file (which causes corruption).
  2. **Off-Server Copy:** A scheduled daily script that pushes the generated backup file to off-server object storage (e.g., S3, Cloudflare R2, verify before use).
  3. **Documented Restore Test:** The repository documentation must include a clear, step-by-step procedure verifying that a backup file can be restored into a local database and verified in under 10 minutes.

---

## 9. Operational Escalation Signals (`escalation_signals`)

The optional profile field `escalation_signals` allows operational telemetry from real-world usage to trigger targeted capability upgrades:

| Signal | Meaning | Evaluated Effect in Repository |
| :--- | :--- | :--- |
| **`sqlite_lock_contention`** | Multiple simultaneous write requests trigger `sqlite3.OperationalError: database is locked`. | Forces `postgres: true`. Scaffolds migration from SQLite to PostgreSQL. |
| **`slow_sync_calls`** | Synchronous external API calls (e.g. emails, PDF generation) exceed 3-second HTTP timeouts. | Forces `background_jobs: true` and `redis: true`. Scaffolds task queue worker. |
| **`high_traffic_bursts`** | Traffic spikes or bot enumeration trigger sudden request bursts. | Forces `redis: true` and `rate_limiting: true`. Scaffolds in-memory rate limiter. |

---

## 10. Developer Overrides Protocol

Developers may manually set capabilities to values different from their derived defaults via the optional `overrides` list in `project.profile.yaml`:
```yaml
overrides:
  - capability: docker
    value: true
    reason: "Solo developer requires containerized workflow matching staging parity."
```

### 10.1 Override Rules
1. **Audience Eligibility:**
   - `senior_developer`: Full override authority.
   - `junior_developer`: Permitted, but the LLM must record an explicit architectural trade-off warning in `DECISIONS-FOR-FOUNDER.md`.
   - `non_technical_founder`: **Overrides are strictly prohibited.**
2. **Matching Requirement:** A capability may differ from its derived value only if a matching entry exists in `overrides` with a technical `reason` of at least 10 characters.
3. **Inviolable Safety Floors (NEVER Overridable):**
   - `minimum_viable_backup`: If `validation_stage` is `validated_pre_revenue`, `paying_customers`, or `scaling`, `minimum_viable_backup` **cannot be overridden to `false`**.
   - `compliance_checklist`: If `data_sensitivity` is `payments_direct` or `health`, `compliance_checklist` **cannot be overridden to `false`**.
   - `hosting_target: paas_ephemeral` with SQLite: Cannot be overridden to allow deployment without volume mount or managed database.

---

## 11. Regional & Country Verification (`founder_region`)

Payment processor availability, tax collection regulations (sales tax, VAT, GST), and data privacy laws vary widely by country.

If `founder_region` is provided (e.g. `US`, `EU`, `GB`, `CA`, `IN`):
1. **Verification Requirement:** The LLM must verify that recommended third-party services operate in the founder's region before suggesting them (verify before use).
2. **Tax & Merchant Model:** When selling digital services internationally, the LLM should recommend a Merchant of Record (e.g. LemonSqueezy, verify before use) to handle global VAT One-Stop Shop (OSS) remittance (verify current rules), after verifying regional availability.
3. **Inability to Verify:** If the LLM cannot verify availability or legal compliance for the specified region with confidence, it **must explicitly state its limitation** and instruct the user to verify local banking and merchant availability.

---

## 12. Budget Conflict Detection & Guidance

The profile field `budget_range` accepts values: `["zero", "bootstrap", "growth", "high"]`. Budget never overrides derived technical architecture without recorded explanation in `DECISIONS-FOR-FOUNDER.md`.

### Conflict Rule 1: Derived `medium` with `budget_range: "zero"`
- **Detection:** `derived_scope == "medium"` AND `budget_range == "zero"`.
- **LLM Behavior:** Present a clear advisory:
  > *"Your project's requirements (e.g., user count) indicate a Medium scope, which normally uses managed PostgreSQL and Redis. Because your budget is $0, you can either: (1) start on free cloud tiers (verify provider free tiers before use), or (2) temporarily remain on single-process SQLite until early revenue is validated."*

### Conflict Rule 2: Derived `medium` with `budget_range: "bootstrap"`
- **Detection:** `derived_scope == "medium"` AND `budget_range == "bootstrap"`.
- **LLM Behavior:** Present a budget guidance advisory:
  > *"Your project requires Medium scope (e.g., PostgreSQL, background workers), which typically requires a growth budget ($50–$500/month, verify before use). With a bootstrap budget (<$50/month), verify PaaS pricing (e.g. starter hobby tiers on Render, Fly.io, or low-cost VPS, verify before use) before provisioning, or keep synchronous execution until revenue supports managed add-ons."*

### Conflict Rule 3: Derived `enterprise` with `budget_range in ["zero", "bootstrap"]`
- **Detection:** `derived_scope == "enterprise"` AND `budget_range in ["zero", "bootstrap"]`.
- **LLM Behavior:** Present a critical conflict notice:
  > *"Enterprise requirements cannot be hosted under a $0 or bootstrap budget. We recommend scoping down to non-sensitive test data first under small scope."*
