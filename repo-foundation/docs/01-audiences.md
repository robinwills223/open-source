# Audiences & Interaction Models

This repository serves three distinct user personas. To ensure everyone receives an experience matched to their expertise, the LLM interface alters its tone, depth of explanation, number of required decisions, and operational guardrails based on the detected audience.

---

## 1. Single Intake Question for Audience Detection

When starting an intake conversation, the LLM asks exactly **one** multiple-choice question:

> **"Which of the following best describes your background and how you want to work on this project?"**
> 1. **Founder / Domain Expert:** I understand the business problem and user needs, but I do not write code. I want simple explanations and automated, sensible technical defaults.
> 2. **Junior Developer / Learner:** I understand programming basics (syntax, Git, simple APIs), but I want guided architectural patterns, explanations of best practices, and protection from common pitfalls.
> 3. **Senior Developer / Lead:** I know modern architecture and deployment workflows. I want fast, unbloated scaffolding, concise answers, and direct control over technical decisions.

Mapping:
- Option 1 &rarr; `non_technical_founder`
- Option 2 &rarr; `junior_developer`
- Option 3 &rarr; `senior_developer`

---

## 2. Audience Profiles

### Audience A: Non-Technical Founder
- **What they know:** Deep knowledge of the business problem, target customer pain points, market context, and desired user workflows. Unfamiliar with software architecture, database migrations, servers, or web protocols.
- **What they want:** A working, testable product as quickly and inexpensively as possible, with zero confusing jargon, clear milestones, and minimal maintenance overhead.
- **How the repo behaves:**
  - Speaks entirely in plain business and product terms.
  - Translates technical terms into functional metaphors on first use.
  - Makes all safe technical decisions automatically without asking, recording each in `DECISIONS-FOR-FOUNDER.md`.
  - Limits intake to the single audience question plus at most 5 high-level functional questions.
  - Overrides are **strictly disabled** for founders.
- **Example Scenario:**
  > *Elena runs a boutique logistics consultancy.* She needs a private web portal where client shippers can paste a manifest and get an immediate emissions calculation report. The repo guides Elena with 5 plain questions, generates a single-server Django app with SQLite, sets up hosted Stripe Checkout, records safe defaults in `DECISIONS-FOR-FOUNDER.md`, and keeps background queues off.

---

### Audience B: Junior Developer
- **What they know:** Basic Python syntax, fundamental HTML/CSS, Git commands, and basic relational database concepts. May lack hands-on experience with production deployment, state management, security boundaries, and modular software design.
- **What they want:** Clear architectural guidance, readable idiomatic code, constructive explanations of *why* choices are made, and protection from dangerous anti-patterns.
- **How the repo behaves:**
  - Uses standard engineering terms with educational context.
  - Prompts for key technical decisions across 5 to 8 questions; records technical preferences in `DECISIONS-FOR-FOUNDER.md`.
  - Allows developer overrides via the `overrides` field in `project.profile.yaml`, but displays and records an architectural trade-off warning in `DECISIONS-FOR-FOUNDER.md`.
  - Inviolable safety floors (MVB, compliance, ephemeral PaaS safeguards) cannot be overridden.
- **Example Scenario:**
  > *Marcus is a junior engineer at a startup.* He is building an internal inventory tracker. The repo guides Marcus through an educational 6-question intake, scaffolds a clean Django model design with unit tests, explains Django's built-in Admin, and allows him to toggle custom flags while warning him against premature microservices.

---

### Audience C: Senior Developer
- **What they know:** Full software development lifecycle, distributed systems, relational data modeling, CI/CD pipelines, security baselines, and performance profiling.
- **What they want:** Rapid project scaffolding, zero boilerplate bureaucracy, maximum token efficiency, transparent configuration files, and immediate escape hatches to override defaults.
- **How the repo behaves:**
  - High-density, concise technical communication (minimal prose, code/diff-first).
  - Minimal, configuration-driven intake: presents a template `project.profile.yaml` to fill or confirm.
  - Allows full manual override of any capability via `overrides` (except non-overridable safety floors).
  - Records custom technical preferences in `DECISIONS-FOR-FOUNDER.md`.
- **Example Scenario:**
  > *Sarah is a staff engineer spinning up a billing reconciliation tool.* She knows exactly what PostgreSQL schemas and worker pools she needs. The repo takes her specification, validates her profile, processes her explicit `overrides`, and generates minimal scaffolding in seconds.

---

## 3. How Audience Adapts LLM Behavior

| Dimension | Non-Technical Founder | Junior Developer | Senior Developer |
| :--- | :--- | :--- | :--- |
| **Explanation Depth** | Functional/Plain English. Jargon defined immediately on first use. No raw stack traces without an executive summary. | Educational. Explains technical rationales, standard conventions, and trade-offs. | Dense & Technical. Direct code snippets, command references, and architectural diffs without tutorials. |
| **Intake Questions** | **Audience question + at most 5 questions**. Strict focus on problem, stage, user volume, user actions, and budget. | **5 to 8 questions**. Balances business goals with technical preferences. | **Minimal / Configuration-driven**. Validates template profile directly or asks targeted architectural questions. |
| **Default Decision-Making** | 100% automated safe defaults. The LLM decides without asking, and records each decision in `DECISIONS-FOR-FOUNDER.md`. This record must be shown to the founder at the end of intake. | Guided recommendations. The LLM presents recommended option first, with 1-2 alternatives. | Explicit control. The LLM asks or confirms key architectural choices and respects explicit overrides. |
| **Override Ability** | **Strictly prohibited**. Overrides are not allowed in founder profiles. | **Permitted with Warning**. Overrides allowed in `overrides` list; LLM records trade-off warnings. Safety floors cannot be overridden. | **Complete / Unrestricted** (except safety floors). Senior engineers can force capability states via `overrides`. |
| **Error Handling** | Action-oriented guidance: "Copy this command, press Enter, then check if your browser opens." | Diagnostic guidance: Points out the file, line number, exception type, and explains why it failed. | Raw stack trace with succinct root cause analysis and surgical patch snippet. |

---

## 4. Intake-to-Field Mapping for Founders

The intake process for non-technical founders consists of the initial **audience detection question plus at most 5 plain-language intake questions**. The LLM translates these answers into the formal fields required by `schemas/project.profile.schema.json`.

**Golden Rule:** Never ask a founder to self-classify technical terms (such as `scope_level` or `data_sensitivity`). The LLM infers technical parameters from the founder's description, sets safe defaults, and confirms them in plain English.

| Intake Question | Target Schema Field | Derivation / Mapping Logic | Plain Confirmation to Founder |
| :--- | :--- | :--- | :--- |
| **Q1: Problem & Workflow** ("What does your product do, who uses it, and what problem does it solve?") | `name`<br>`description`<br>`product_shape` | - Generates slug `name` and plain `description`.<br>- **Infers `product_shape`**: waitlist &rarr; `demand_test`; single utility &rarr; `small_tool`; multi-tenant accounts &rarr; `multi_user_saas`. | "We will build a tool called `[name]` for `[purpose]`." |
| **Q2: Current Stage** ("Do you have active users or paying customers today, or is this currently an idea or prototype?") | `validation_stage` | - **Direct question**: idea &rarr; `idea`; building demo &rarr; `prototype`; live beta testers &rarr; `validated_pre_revenue`; active paid users &rarr; `paying_customers`; high growth &rarr; `scaling`. | "We have recorded your stage as `[stage]`." |
| **Q3: Anticipated Users** ("How many active users or customer accounts do you expect over the next 3 to 6 months?") | `expected_users` | - **Infers `expected_users`**: parses numerical estimates (e.g., "around 50 coworkers" &rarr; `50`). | "We have sized the system for up to `[N]` active users." |
| **Q4: Logins & Payments** ("Will users create accounts and log in? Will people pay inside your product, or is it free/internal?") | `data_sensitivity` | - **Plain behavior mapping**:<br>  - No accounts/free &rarr; `none`.<br>  - Users log in with email/passwords &rarr; `personal`.<br>  - Users pay inside the app &rarr; `payments_hosted` (uses external hosted checkout like Stripe Checkout or LemonSqueezy).<br>  - Medical/patient data &rarr; `health` (triggers enterprise halt).<br>  - **Rule:** Never offer "direct card handling" to founders. `payments_direct` is never inferred for a founder. | "Your app handles `[logins / hosted payments]`. Credit card numbers will never touch your server." |
| **Q5: Budget & Region** ("What is your monthly budget for hosting, and what country/region is your business based in?") | `budget_range`<br>`founder_region` | - Maps budget: $0 &rarr; `zero`; <$50/mo &rarr; `bootstrap`; $50–$500/mo &rarr; `growth`; >$500/mo &rarr; `high`.<br>- Maps region code (e.g., "US", "EU", "GB"). | "We will target hosting within the `[budget_range]` budget tier in region `[founder_region]`." |

### Inferred Value Confirmation & Cautious Default Rule
- **Confirmation Rule:** Before an inferred value raises `scope_level` or enables a capability, the LLM must state it in plain words and obtain confirmation.
- **Cautious Default:** When an inferred value is uncertain, default to the most cautious *plausible* option (e.g. `personal` if logins are ambiguous, `validated_pre_revenue` if beta users are testing), then confirm with the user.

### Safe Technical Defaults (Decided Without Asking)
The following fields are not asked of founders and are populated automatically:
- `stack`: Set to `"django"` (established baseline).
- `team_size`: Set to `1` (solo founder) unless multiple engineers are explicitly stated.
- `hosting_target`: Decided deterministically without asking based on `budget_range` and `validation_stage` per [`docs/05-rules-single-source.md` Section 7](05-rules-single-source.md#7-deterministic-hosting-target-inference).
- `scope_level`: **Computed deterministically** from `expected_users`, `data_sensitivity`, and `validation_stage` via [`docs/05-rules-single-source.md`](05-rules-single-source.md#1-scope-level-derivation--the-highest-signal-wins-rule). Note that `team_size` is decoupled.
- `capabilities`: **Evaluated deterministically** via [`docs/05-rules-single-source.md#6-authoritative-capability-trigger-matrix`](05-rules-single-source.md#6-authoritative-capability-trigger-matrix).
- **Mandatory Reporting:** Every decision made without asking must be recorded in plain words in `DECISIONS-FOR-FOUNDER.md` and presented to the founder at the end of intake.

---

## 5. Intake Protocols for Developers

### Junior Developer Intake (5 to 8 Questions)
1. Problem, target users, and domain models.
2. Current stage and immediate milestones.
3. User scale and expected concurrency.
4. Data sensitivity and authentication style (session vs token).
5. Architecture preferences (Django templates + HTMX vs decoupled API).
6. Testing scope (model unit tests, API integration tests).
7. Hosting target, budget, and deployment preferences.
8. Team size and CI workflow preferences.

*Note on Technical Preferences:* Architectural preferences (templates vs API, authentication style, test scope) are recorded in `DECISIONS-FOR-FOUNDER.md`, **not** in `project.profile.yaml`.

### Senior Developer Intake (Configuration-Driven)
The LLM presents a template `project.profile.yaml` for the senior engineer to fill, paste, or review. If the developer wants custom switches, they include an `overrides` block. Any custom architectural conventions are documented in `DECISIONS-FOR-FOUNDER.md`.
