# Architecture Decision Log & Default Conventions

This document records the architectural choices made during the design of `repo-foundation`, the rationale behind each decision, rejected alternatives, and resolved default conventions. All provider recommendations and pricing references are marked **verify before use**.

---

## 1. Design Decisions Log

### DEC-001: Tool-Agnostic File Formats (Markdown, YAML, JSON)
- **Decision:** All documentation, schemas, and configurations are maintained strictly in standard Markdown, JSON Schema (draft-07), and YAML.
- **Why:** Ensures cross-compatibility across all LLMs and MCP integration without proprietary wrappers.

### DEC-002: Django as the Foundation Stack
- **Decision:** Locked `stack` to `["django"]` for the initial release.
- **Why:** Django provides a battle-tested batteries-included foundation with built-in security, ORM, and admin portal.

### DEC-003: Progressive Disclosure & Zero-Debt Capabilities (OFF by Default)
- **Decision:** Every capability is **OFF by default**.
- **Why:** Prevents premature infrastructure debt. Complexity must be earned through verified profile metrics.

### DEC-004: Single-Question Audience Calibration
- **Decision:** Classify the user into one of three personas (`non_technical_founder`, `junior_developer`, `senior_developer`) using exactly one multiple-choice question at intake.
- **Why:** Immediately establishes tone, question count, and guardrail strictness.

### DEC-005: Decoupling Product Shape from Scope Level
- **Decision:** Separated the functional nature of the software (`demand_test`, `small_tool`, `multi_user_saas`) from its operational scale (`small`, `medium`, `enterprise`).
- **Why:** Allows a multi-tenant SaaS to launch as an early prototype on small, low-cost infrastructure.

### DEC-006: Honest Security & Compliance Posture ("Baseline")
- **Decision:** Strict prohibition of claims that generated code is "secure" or "compliant." The term "baseline" is used exclusively.
- **Why:** Avoids dangerous legal and ethical misrepresentations.

### DEC-007: Enterprise Scope Marked as "Defined, Not Yet Implemented"
- **Decision:** Documented the Enterprise tier's specifications in `02-product-shapes-and-scope.md` but marked it as not yet implemented.
- **Why:** Outlines architectural evolution without introducing premature unverified enterprise scaffolding.

### DEC-008: Capability Activation: Triggers Alone Decide
- **Decision:** Removed the "Allowed Tiers" column from capability definitions. Triggers alone decide capability states.
- **Why:** Eliminates contradictions between tier gating and explicit trigger conditions.

### DEC-009: Permitted vs. Active Distinction
- **Decision:** Product shapes define what architectural patterns are **PERMITTED** in the codebase; capability switches define what is **ACTIVE** at runtime.
- **Why:** Resolves contradiction where SaaS designs include background workers, but switches keep them inactive until triggered.

### DEC-010: Exclusive Single Source of Truth for Rules & Non-Overlapping Boundaries
- **Decision:** Created [`docs/05-rules-single-source.md`](05-rules-single-source.md) as the sole authority for move-up rules, scope boundaries, and capability triggers.
- **Why:** Eliminates duplicate, drifting definitions across docs 02 and 04.

### DEC-011: Decoupling `team_size` from Scope Level Derivation
- **Decision:** `scope_level` derives strictly from `expected_users`, `data_sensitivity`, and `validation_stage`. `team_size` directly drives only `ci` and `docker`.
- **Why:** Multi-developer collaboration on a prototype does not require PostgreSQL or Redis; it only requires Git CI and container parity.
- **Rejected Alternative:** Keeping `team_size` in the scope max() function. Rejected because it forced multi-developer prototypes into medium-tier cloud hosting prematurely.

### DEC-012: Budget Conflict Advisory & Renaming "enterprise" Budget to "high"
- **Decision:** Renamed budget tier `enterprise` to `high`. Established explicit conflict advisory warnings when derived scope exceeds budget, recorded in `DECISIONS-FOR-FOUNDER.md`.
- **Why:** Resolves namespace collision and gives founders clear cost visibility.

### DEC-013: Ephemeral PaaS SQLite Safeguards
- **Decision:** Added a mandatory rule that if `hosting_target == "paas_ephemeral"` and database is SQLite, deployment is strictly invalid in schema unless resolved with a persistent volume or managed PostgreSQL database.
- **Why:** Ephemeral containers wipe disk state on redeploy, permanently erasing SQLite databases.
- **Rejected Alternative:** Upgrading any PaaS project to PostgreSQL without asking or explaining alternatives. Rejected because persistent disk volumes allow low-cost, zero-maintenance SQLite deployment for small budgets.

### DEC-014: Minimum Viable Backup (MVB) from Beta Stage Onward
- **Decision:** Added an independent `minimum_viable_backup` requirement active from `validation_stage: validated_pre_revenue` onward, requiring SQLite native backup commands (`.backup` or `VACUUM INTO`), off-server storage, and a documented restore test.
- **Why:** Waiting for paying customers left beta users exposed to data loss. Raw file copying of active SQLite files causes corruption, so native commands are mandatory.

### DEC-015: Granular Payment Sensitivity (`payments_hosted` vs `payments_direct`)
- **Decision:** Split payment sensitivity into `payments_hosted` and `payments_direct`. Only `payments_direct` triggers heavy compliance checklists.
- **Why:** Hosted checkout (Stripe Checkout, LemonSqueezy) keeps cardholder data off the server, avoiding heavy PCI DSS cardholder environment audits.

### DEC-016: Transparent Decision Recording (`DECISIONS-FOR-FOUNDER.md`)
- **Decision:** Technical defaults decided without asking are recorded exclusively in `DECISIONS-FOR-FOUNDER.md`, which must be presented at the end of intake.
- **Why:** Clean separation of machine-readable profile data from human-readable architectural explanations.

### DEC-017: Regional & Country Verification (`founder_region`)
- **Decision:** Added an optional `founder_region` field to the profile schema and mandated that the LLM verify gateway and tax compliance for the region before recommending providers (verify before use).
- **Why:** Payment processors and VAT/sales tax rules vary dramatically across jurisdictions.

### DEC-018: Hosting Target Inference & Recording
- **Decision:** `hosting_target` is a required field inferred deterministically from `budget_range` and `validation_stage` per `docs/05` Section 7, recorded in `DECISIONS-FOR-FOUNDER.md`.
- **Why:** Zero-budget live products with real users cannot be hosted reliably on a local machine, prompting a recorded budget advisory.

### DEC-019: Behavior When Derived Scope is Enterprise
- **Decision:** When `scope_level` derives to `enterprise`, the LLM halts scaffolding, states plainly that enterprise architecture is not yet implemented, explains why, and offers a scoped-down non-sensitive prototype.
- **Why:** Scaffolding enterprise apps without hardened SAML and audit infrastructure creates dangerous false security expectations.

### DEC-020: Operational Escalation Signals (`escalation_signals`)
- **Decision:** Introduced an optional `escalation_signals` list in the profile that maps measured runtime bottlenecks directly to capability upgrades.
- **Why:** Bridges runtime production monitoring to declarative capability activation.

### DEC-021: Evidence-Based Heavy Infrastructure
- **Decision:** Decoupled `background_jobs` and `redis` from general user estimates. `background_jobs` requires measured `slow_sync_calls`. `redis` requires `background_jobs == true` or `high_traffic_bursts`. Added `product_shape == "multi_user_saas"` to `rate_limiting` triggers.
- **Why:** Queues and caches add daemon processes, network hops, and operational points of failure. They should answer measured bottlenecks, not speculative traffic projections.
- **Rejected Alternative:** Automatically enabling Redis for all Medium-scope projects. Rejected because many Medium-scope SaaS tools perform simple synchronous CRUD where external in-memory brokers add unneeded hosting expense.

### DEC-022: Developer Overrides Protocol
- **Decision:** Added an optional `overrides` array of `{capability, value, reason}` (reason minLength 10). Permitted for `junior_developer` (with recorded warning) and `senior_developer`. Prohibited for `non_technical_founder`. Inviolable safety floors (MVB, compliance, ephemeral PaaS safeguards) are strictly non-overridable.
- **Why:** Empowers experienced engineers to customize technical architectures without permitting non-technical founders to disable essential safety baselines.
- **Rejected Alternative:** Allowing founders to override capabilities through conversational prompts. Rejected because founders cannot assess the DevOps maintenance burden or security risks of premature infrastructure.

### DEC-023: Invalidation of Ephemeral PaaS SQLite Deployments
- **Decision:** Enforced a schema-level validation rule where `hosting_target == "paas_ephemeral"` with `capabilities.postgres == false` is strictly invalid.
- **Why:** Prevents non-persistent container deployments from ever being scaffolded with SQLite, which guarantees data loss on restart.

### DEC-024: Founder Intake Behavioral Focus & Prohibition of `payments_direct`
- **Decision:** Rewrote founder intake Q4 as plain behavioral questions about logins and customer payments. Never offer direct card handling as an option to founders. `payments_direct` is never inferred for a founder.
- **Why:** Modern SaaS products should use hosted checkout sessions. Handling raw credit card numbers creates severe PCI DSS liability that non-technical founders should never take on.

### DEC-025: Dual-Representation of Rules (Prose in docs/05 vs. Code in tools/rules.py) and Drift Mitigation
- **Decision:** Implemented an executable reference implementation in `tools/rules.py` citing `docs/05` sections, backed by a table-driven `pytest` test suite.
- **Context & Risk of Drift:** Rules now exist in two representations: human-readable prose in `docs/05-rules-single-source.md` and executable logic in `tools/rules.py`. While `docs/05` remains the strict architectural authority, having dual representations introduces the risk of subtle divergence or drift during future updates.
- **Mitigation & Future Plan:** In the current phase, full parity is maintained by citing exact `docs/05` sections in `tools/rules.py` and verifying both against comprehensive boundary test tables and profile fixtures. In a future phase, a single machine-readable specification file (e.g. `rules.yaml` or `rules.json`) will become the single source, with documentation markdown tables in `docs/05` and executable validators in `tools/rules.py` automatically generated or verified via automated schema synchronization.

### DEC-026: Django LTS Pinning (`Django==5.2.9`) and Python Compatibility
- **Decision:** Pinned `Django==5.2.9` in `templates/django-small-tool/requirements.txt`.
- **Why & What Was Checked:** Queried PyPI release registry and verified that Django 5.2 is the current long-term support (LTS) release line, with official upstream security support extending through 2028. Verified official Python version support covers Python 3.10, 3.11, 3.12, and 3.13, matching our toolchain constraints.
- **Rejected Alternatives:** Leaving Django unpinned or floating (`Django>=5.0`), which would risk silent breaking changes in downstream generated projects.

### DEC-027: Zero-JavaScript Policy in v0.1 Starter Template
- **Decision:** Built the v0.1 small-tool template using strictly server-rendered Django templates and a minimal CSS stylesheet. No JavaScript, HTMX, or npm build pipelines are included.
- **Why:** The initial small-tool starter focuses on rock-solid fundamentals: login, ownership isolation, CRUD, and data export. Adding HTMX or Alpine.js at this stage would introduce frontend complexity before a concrete workflow requires dynamic in-page updates.
- **Future Pathway:** HTMX and Alpine.js remain the resolved default for interactive widgets (see DEC-018 / Section 2.3), and will be introduced when specific interactive workflows require client-side reactivity.

### DEC-028: Generator Strict Support Boundary and Unsupported Profile Behavior
- **Decision:** In `tools/generate_project.py`, enforce strict support boundaries: v0.1 supports exclusively `stack: django`, `product_shape: small_tool`, `scope_level: small`, and zero optional capabilities (only `minimum_viable_backup` is permitted). Any profile triggering optional capabilities (such as `team_size: 2` triggering `docker` and `ci`, or SaaS shapes) causes the generator to halt with exit code 2 and a plain explanation.
- **Why:** Prevents generating partial, broken, or misleading codebases that lack required infrastructure services. A user must never be given a project that silently omits configured profile capabilities.

### DEC-029: Generic "Records Tracker" Archetype and Ownership Isolation
- **Decision:** Standardized the v0.1 starter workflow around a generic "Records Tracker" model (`title`, `notes`, `status`, `created_at`, `updated_at`, `user`).
- **Why:** Every small tool is fundamentally a data capture and retrieval problem. Providing a working end-to-end model with forms, status filtering, and strict user ownership isolation (`get_object_or_404(Record, pk=pk, user=request.user)`) gives non-technical founders and LLM assistants a clean archetype to customize.

### DEC-030: Formula-Injection Sanitization in CSV Exports
- **Decision:** Enforced spreadsheet formula injection sanitization in CSV exports (`records/views.py`), prepending a single quote `'` to any cell beginning with `=`, `+`, `-`, `@`, `\t`, or `\r`.
- **Why:** Protects founders and users from client-side spreadsheet formula execution attacks when exporting user-submitted text data into Excel, Google Sheets, or LibreOffice Calc.

---

## 3. Open Architectural Questions for Future Milestones

### OPEN-Q-001: Scaffolding Pathway for `demand_test` Shapes
- **Question:** How should `demand_test` (landing page / waitlist) products be scaffolded in v0.2?
- **Discussion:** In v0.1, `demand_test` is halted because the scaffold provides a full CRUD records workflow. Should `demand_test` provide a stripped-down single-model waitlist email collector within Django, or use a static generator?

### OPEN-Q-002: Packaging of Automated Backup Routines for Small Tools
- **Question:** How should `minimum_viable_backup` scripts be packaged when moving beyond v0.1?
- **Discussion:** In v0.1, MVB is noted as a manual requirement for live beta users. In v0.2, should we bundle a standalone Python script invoking SQLite's native `.backup` API with S3/R2 upload, or rely on PaaS volume snapshot integrations?

---

## 2. Resolved Defaults for Future Phases

The four core technical questions for stack evolution are resolved with the following standard defaults (all provider recommendations and pricing are estimates, verify before use):

### 1. Database Migration Pathway (SQLite &rarr; PostgreSQL)
- **Standard Default:** Use Django's native serialization commands with exclusion of system tables:
  ```bash
  python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > datadump.json
  # Switch DATABASES setting to PostgreSQL in settings.py, run migrations, then:
  python manage.py loaddata datadump.json
  ```
- **Large Dataset Alternative:** For databases exceeding 500MB where JSON serialization is memory-prohibitive, use `pgloader` with a configured `.load` file.

### 2. Opinionated Default PaaS Target
- **Standard Default:** Recommend **Render** (or **Fly.io** when persistent SQLite volume mounts are required, verify before use) as the primary PaaS target.
- **Swap Notes:** Document swap recipes for Railway (simple Docker PaaS), Heroku, and Ubuntu VPS running Gunicorn under systemd with Caddy reverse proxy.

### 3. Front-End Interactivity & Templating
- **Standard Default:** **Django native templates + HTMX + Alpine.js**.
- **Rationale:** Preserves a unified Python/HTML codebase, eliminates Node.js/npm dependencies, prevents complex API serializer duplication, and allows founders to build responsive interactive workflows with zero JavaScript build toolchains.

### 4. Payment Gateway Architecture
- **Standard Default:** Recommend a **Merchant of Record** (such as LemonSqueezy or Paddle, verify before use) for international SaaS sales, after verifying `founder_region` availability.
- **Rationale:** Merchants of Record handle global sales tax calculation, EU VAT One-Stop Shop (OSS) remittance (verify current rules), and international billing compliance on behalf of the founder, reducing substantial tax compliance overhead. For founders selling exclusively in their home country with existing tax registration, Stripe Checkout remains the standard alternative.
