# Repo Foundation

> [!WARNING]
> **ALPHA RELEASE:** This project is in active alpha development (v0.1.0-alpha). Expect breaking changes to schemas, generator commands, and configuration formats between releases.

Repo Foundation is an open-source guide and deterministic scaffolding tool that takes non-technical founders, junior developers, and senior developers from an initial idea to a tested, running local product using an LLM as the interface.

---

## Who It Is For

- **Non-Technical Founders:** You have a specific customer problem to solve but do not write software. You receive plain-language guidance, safe minimal defaults, and an immediate working prototype without technical jargon.
- **Junior Developers:** You know programming fundamentals but need guidance on production architectures. You receive clear explanations of why specific capabilities are chosen, clean patterns, and a tested starter codebase.
- **Senior Developers:** You want to skip repetitive initial project wiring and enforce architectural discipline. You get a machine-readable profile, full override authority, and a zero-fluff starter project with zero hidden dependencies.

---

## What It Does Today (v0.1)

1. **Intake:** The LLM asks at most five conversational questions to understand your users, validation stage, and data sensitivity.
2. **Validated Profile:** Generates a deterministic `project.profile.yaml` adhering to strict architectural schema rules.
3. **Scaffold Generation:** Generates a clean, working Django small-tool starter that runs locally with its own automated tests passing out of the box.

---

## What It Does NOT Do Yet

The v0.1 release focuses strictly on local single-process tools. It does not yet include:
- Medium or enterprise scope architectures (no PostgreSQL, Redis, Celery background workers, or multi-tenant isolation).
- Cloud deployment automation or infrastructure-as-code recipes (no Docker, Kubernetes, or automated PaaS push).
- Model Context Protocol (MCP) server endpoints or external tool plugins.
- Autonomous sub-agent swarms, custom agent loops, or background worker bots.
- Standalone browser web UI interfaces for repository management.
- Custom customization skills, event hooks, or sidecar extensions.

---

## Quick Start for Non-Technical Founders

1. Download or clone this repository to your computer.
2. Open the `repo-foundation` folder in your preferred LLM coding tool (such as Claude Code, ChatGPT, Cursor, or Antigravity).
3. Type this exact message into your chat:
   > *"Help me test my idea using this repo."*

**What happens next:**
The LLM will greet you and ask four to five simple questions about your product idea, how many users you expect, and whether you handle payments. It will then generate a tailored project profile and verify that only the tools your project actually needs are turned on. Finally, it will generate a clean starter application in a new folder and walk you through running it on your own computer with one-click commands. You can click through and verify your workflow in your browser right away.

---

## Quick Start for Developers

```bash
# 1. Install development tooling dependencies
python -m pip install -r requirements-dev.txt

# 2. Validate a profile specification (returns exit code 0 if valid)
python tools/validate_profile.py examples/profiles/valid/small-paid-tool.yaml

# 3. Generate a local Django starter from the profile
python tools/generate_project.py examples/profiles/valid/small-paid-tool.yaml ./my-tool

# 4. Run the generated project's own automated tests
cd my-tool && python manage.py test
```

---

## Honest Baseline Limits

- **Baseline Only:** This repository provides defensible architectural starting points, not formal guarantees of security or regulatory compliance.
- **Not Legal Advice:** Checklists and Merchant-of-Record recommendations do not substitute for qualified legal, tax, or cybersecurity counsel.
- **Review Required:** Generated code and LLM recommendations must be reviewed and tested by a human before deploying to production.
- **Single-Node Local Focus:** Version 0.1 runs on your local machine; production hosting requires setting up persistent storage and production credentials.

---

## Architectural Documentation & Policies

- [`docs/00-vision.md`](docs/00-vision.md): Purpose, intended audience, and non-goals.
- [`docs/01-audiences.md`](docs/01-audiences.md): Personas, intake protocols, and LLM behavioral adaptation.
- [`docs/02-product-shapes-and-scope.md`](docs/02-product-shapes-and-scope.md): Product shapes, operational scopes, and move-up rules.
- [`docs/03-profile-schema.md`](docs/03-profile-schema.md): Profile schema fields, constraints, and JSON Schema mapping.
- [`docs/04-capability-switches.md`](docs/04-capability-switches.md): Rationales for all ten capability switches.
- [`docs/05-rules-single-source.md`](docs/05-rules-single-source.md): The sole authoritative source for scope derivation, triggers, and safeguards.
- [`docs/guides/run-locally.md`](docs/guides/run-locally.md): Beginner local execution and troubleshooting guide.
- [`docs/guides/what-you-get.md`](docs/guides/what-you-get.md): Breakdown of starter workflow and baseline protections.
- [`docs/testing/cold-start-test.md`](docs/testing/cold-start-test.md): Standardized usability observation protocol.
- [`docs/DECISIONS.md`](docs/DECISIONS.md): Architectural Decision Records (ADRs).
- [`CONTRIBUTING.md`](CONTRIBUTING.md): How to run tests and propose profile fixtures.
- [`SECURITY.md`](SECURITY.md): Vulnerability reporting policy and scope boundaries.
