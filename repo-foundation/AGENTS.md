# Agent Instructions: Operating Rules for LLMs

These rules govern how any Large Language Model (Antigravity, Claude, Codex, GPT, etc.) interacts with this repository. You must follow these principles strictly across all conversations and scaffolding tasks.

---

## 1. Prime Directive, Lazy Loading & Profile Change Protocol
- **Read the Profile First:** Inspect `project.profile.yaml` before proposing architecture or scaffolding.
- **Lazy Loading:** After reading the profile, open only the specific docs and sections needed for the immediate step. Do not dump all documentation into context.
- **Profile Change Protocol:** To change capabilities, architecture, or scope: (1) update `project.profile.yaml` first, (2) re-run the validation checklist, (3) record the change and rationale in `DECISIONS-FOR-FOUNDER.md`, and (4) only then modify code.
- If `project.profile.yaml` does not exist, conduct intake (Section 3) to produce and validate it. Never scaffold code until the profile exists and is valid.

---

## 2. Zero-Debt Capability Enforcement & Developer Overrides
- **All capabilities are OFF by default.**
- **Strict Signal Matching:** Never enable a capability unless its exact trigger in [`docs/05-rules-single-source.md#6-authoritative-capability-trigger-matrix`](docs/05-rules-single-source.md#6-authoritative-capability-trigger-matrix) evaluates to `true`.
- **Permitted vs. Active:** Product shape defines what is permitted; capability switches define what is active.
- **Transparent Decisions:** The LLM decides technical details **without asking**, and records each decision in `DECISIONS-FOR-FOUNDER.md`, shown to the founder at the end of intake.
- **Developer Overrides:** Allowed only for `junior_developer` (with recorded warning) or `senior_developer` via the `overrides` field (`{capability, value, reason}`). Non-technical founders cannot override.
- **Inviolable Safety Floors:** MVB for stage $\ge$ `validated_pre_revenue`, compliance checklist for `payments_direct`/`health`, and ephemeral-PaaS SQLite safeguards **cannot be overridden to `false`**.
- **Enterprise Handling:** If derived scope is `enterprise`, state plainly that enterprise scaffolding is not yet supported in this repository, explain why, offer a scoped-down non-sensitive prototype, and do not scaffold.

---

## 3. Intake Protocols by Audience

Begin intake with the single audience question from [`docs/01-audiences.md`](docs/01-audiences.md). Then adapt:
- **Senior Developer:** Minimal, configuration-driven intake. Presents a profile template to fill or confirm. Overrides placed in `overrides`. Technical preferences recorded in `DECISIONS-FOR-FOUNDER.md`.
- **Junior Developer:** 5 to 8 questions balancing business goals and coding conventions per [`docs/01-audiences.md`](docs/01-audiences.md). Technical preferences recorded in `DECISIONS-FOR-FOUNDER.md`, not the profile.
- **Non-Technical Founder:** Ask the audience question plus **at most 5 intake questions**:
  1. *Problem & Workflow:* Product purpose and target user. (Infers `name`, `description`, `product_shape`).
  2. *Current Stage:* Users or revenue today? (Directly sets `validation_stage`).
  3. *Anticipated Users:* Active accounts over next 3–6 months. (Infers `expected_users`).
  4. *Logins & Payments:* "Will users create accounts and log in? Will people pay inside your product?" Never offer direct card handling. (Infers `data_sensitivity`: `none`, `personal`, or `payments_hosted`).
  5. *Budget & Region:* Monthly hosting budget and business country/region. (Sets `budget_range`, optional `founder_region`).

### Inferred Value Confirmation & Cautious Default Rule
- **Confirmation Rule:** Before an inferred value raises `scope_level` or enables a capability, state it in plain words and get user confirmation.
- **Cautious Default:** When an inferred value is uncertain, default to the most cautious *plausible* option, then confirm with the user.

### Safe Technical Defaults (Decided Without Asking)
- `profile_version`: Set to `1`. `stack`: `"django"`. `team_size`: `1` (unless multiple engineers explicitly stated).
- `hosting_target`: Inferred deterministically from `budget_range` and `validation_stage` per [`docs/05-rules-single-source.md` Section 7](docs/05-rules-single-source.md#7-deterministic-hosting-target-inference), recorded in `DECISIONS-FOR-FOUNDER.md`.
- `scope_level`: **Computed deterministically** from `expected_users`, `data_sensitivity`, and `validation_stage` via `docs/05`. (`team_size` is decoupled from scope derivation).
- `capabilities`: Evaluated deterministically via `docs/05`. All 10 keys required.

---

## 4. Chat-Only Profile Validation Checklist
For an LLM in a pure chat session without terminal access, verify all rules before writing the profile:
1. **Required Fields:** All 13 required fields present (`profile_version`, `name`, `audience`, `product_shape`, `scope_level`, `stack`, `expected_users`, `team_size`, `data_sensitivity`, `budget_range`, `validation_stage`, `hosting_target`, `capabilities`).
2. **Allowed Values:** `profile_version: 1`, `founder_region` matches `^([A-Z]{2}|EU)$`, `hosting_target` valid enum, `escalation_signals` valid subset.
3. **Deterministic Scope Check:** `scope_level` strictly equals $\max(\text{tier}(\text{expected\_users}), \text{tier}(\text{data\_sensitivity}), \text{tier}(\text{validation\_stage}))$ per `docs/05`. `team_size` must not be included.
4. **Trigger Signal Check:** No capability is `true` without its exact trigger in `docs/05` or a valid matching entry in `overrides`.
5. **Override Validity Check:** Overrides present only for junior/senior developers, with reason $\ge$ 10 chars. Safety floors (MVB, compliance, ephemeral-PaaS) are NOT overridden.
6. **Schema If/Then Invariants:**
   - If `validation_stage` $\in$ `[validated_pre_revenue, paying_customers, scaling]`, `minimum_viable_backup` MUST be `true`.
   - If `data_sensitivity` $\in$ `[payments_direct, health]`, `compliance_checklist` MUST be `true`.
   - If `hosting_target: paas_ephemeral`, `postgres` MUST be `true`.
   - If `"slow_sync_calls"` in `escalation_signals`, `background_jobs` and `redis` MUST be `true`.
   - If `"sqlite_lock_contention"` in `escalation_signals`, `postgres` MUST be `true`.
   - If `"high_traffic_bursts"` in `escalation_signals`, `redis` MUST be `true`.
7. **Safeguard Checks:**
   - If `scope_level: enterprise`, halt scaffolding and offer non-sensitive prototype.

*(Note: A programmatic `validate_profile` tool will be added in the MCP phase.)*

---

## 5. Communication & Explanations
- **Audience Adaptation:** Adapt tone, detail, and depth to the audience in the profile, per [`docs/01-audiences.md`](docs/01-audiences.md).
- **Define Jargon on First Use:** Explain technical terms with real-world metaphors.
- **Honest Security Posture:** Use the word **"baseline"**; never claim a product is "secure" or "compliant."
- **Tool Agnostic:** Maintain pure Markdown, YAML, and JSON.
