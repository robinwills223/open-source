# Capability Switches & Architectural Context

In alignment with the core principle of **Zero-Debt Progressive Disclosure**, every technical capability in this repository is **OFF by default**. Heavy infrastructure components (task queues, cache brokers) are strictly evidence-based and turn on in response to measured production problems rather than speculative user estimates.

Capabilities are never unlocked by assumption, convention, or developer habit.

> [!IMPORTANT]
> **Single Source of Truth:** The authoritative trigger conditions governing when each capability turns ON or OFF are defined exclusively in [`docs/05-rules-single-source.md#6-authoritative-capability-trigger-matrix`](05-rules-single-source.md#6-authoritative-capability-trigger-matrix). This document explains the purpose, defaults, and plain-language rationales for each capability.
>
> **Permitted vs. Active:** A project's product shape defines what architectural patterns are **PERMITTED** in the codebase. An architectural capability is only **ACTIVE** when its switch evaluates to `true` according to the rules in [`docs/05-rules-single-source.md`](05-rules-single-source.md).

---

## 1. Capability Overview & Defaults

Every capability starts in an inactive state (`false`). The table below outlines each switch and the plain-language rationale for why it remains disabled until triggered:

| Capability | Default State | Plain-Language Rationale | Authoritative Trigger Link |
| :--- | :--- | :--- | :--- |
| **`docker`** | **OFF** (`false`) | Containers add tooling and virtualization complexity unnecessary for solo builders on local Python virtualenvs, but needed for team environment consistency. | [Trigger Rule](05-rules-single-source.md#6-authoritative-capability-trigger-matrix) |
| **`postgres`** | **OFF** (`false`) | SQLite requires zero configuration and zero operational maintenance until medium scale or measured lock contention requires PostgreSQL. | [Trigger Rule](05-rules-single-source.md#6-authoritative-capability-trigger-matrix) |
| **`redis`** | **OFF** (`false`) | An external in-memory data store adds cloud hosting costs and connection failure points; enabled only when backing an active job queue or absorbing measured traffic bursts. | [Trigger Rule](05-rules-single-source.md#6-authoritative-capability-trigger-matrix) |
| **`background_jobs`** | **OFF** (`false`) | Detached worker queues answer measured slow synchronous calls (HTTP timeouts >3s), not hypothetical future tasks. | [Trigger Rule](05-rules-single-source.md#6-authoritative-capability-trigger-matrix) |
| **`ci`** | **OFF** (`false`) | Automated GitHub Actions pipelines create maintenance overhead before multiple developers collaborate on pull requests. | [Trigger Rule](05-rules-single-source.md#6-authoritative-capability-trigger-matrix) |
| **`error_monitoring`** | **OFF** (`false`) | Third-party error telemetry tools (such as Sentry, verify before use) require API tokens, external accounts, and outbound network traffic. | [Trigger Rule](05-rules-single-source.md#6-authoritative-capability-trigger-matrix) |
| **`compliance_checklist`** | **OFF** (`false`) | Formal compliance checklists apply only when handling raw cardholder data or health records. Hosted checkout does NOT trigger this. | [Trigger Rule](05-rules-single-source.md#6-authoritative-capability-trigger-matrix) |
| **`rate_limiting`** | **OFF** (`false`) | Request throttling protects public endpoints and multi-user SaaS environments against abuse. | [Trigger Rule](05-rules-single-source.md#6-authoritative-capability-trigger-matrix) |
| **`minimum_viable_backup`** | **OFF** (`false`) | Off-server database copy using SQLite native backup (`.backup` / `VACUUM INTO`) and documented restore test active from beta stage onward. | [Trigger Rule](05-rules-single-source.md#6-authoritative-capability-trigger-matrix) |
| **`backups`** | **OFF** (`false`) | Automated scheduled cloud-managed snapshot routines require cloud storage credentials, retention policies, and verification drills. Supersedes MVB when active. | [Trigger Rule](05-rules-single-source.md#6-authoritative-capability-trigger-matrix) |

---

## 2. Operating Principles for LLMs

1. **Rule of Parsimony:** If a project profile does not satisfy the exact logical trigger defined in [`docs/05-rules-single-source.md`](05-rules-single-source.md#6-authoritative-capability-trigger-matrix), the capability MUST remain `false`.
2. **Never Bundle Capabilities:** Enabling `postgres` does not automatically enable `redis` or `docker`. Each capability evaluates its trigger conditions independently.
3. **Evidence-Based Queues and Caches:** Do not enable background workers or Redis based solely on user estimates. Require explicit escalation signals (`slow_sync_calls`, `high_traffic_bursts`) or formal overrides.
4. **Developer Overrides:** Capabilities may differ from their derived trigger values only if an explicit entry in `overrides` exists for junior or senior developers per [`docs/05-rules-single-source.md` Section 10](05-rules-single-source.md#10-developer-overrides-protocol). Inviolable safety floors can never be overridden.
