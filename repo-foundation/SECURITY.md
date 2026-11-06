# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, please report it privately:

1. **Preferred:** Use GitHub's private vulnerability reporting feature on the repository's **Security** tab under **Advisories**.
2. **Fallback:** If GitHub private reporting is unavailable, email our security point of contact at: `[SECURITY CONTACT]`.

Please include:
- A description of the vulnerability and potential impact.
- Step-by-step instructions or proof-of-concept to reproduce the behavior.
- The version, commit hash, or operating system involved.

We acknowledge receipt on a **best-effort basis** (typically within 3 to 5 business days). As an open-source project maintained by volunteers, patch timelines and release schedules are also best-effort.

---

## Scope

### In Scope
- Core repository validation and derivation tools in `tools/` (`rules.py`, `validate_profile.py`, `check_links.py`, `check_repo_hygiene.py`, `generate_project.py`).
- Schema validation rules in `schemas/project.profile.schema.json`.
- The reference Django small-tool project template (`templates/django-small-tool/`).
- Vulnerabilities where the repository tooling produces unsafe baseline configurations without warning.

### Out of Scope
- Individual applications deployed or modified by end users using generated scaffolds.
- Third-party hosting environments, cloud providers, or platform-as-a-service configurations.
- Vulnerabilities in third-party dependencies (e.g. Django, Python, OS packages) that have upstream security channels.
- Denial of Service (DoS) attacks against local development servers.

---

## Baseline Posture & Disclaimer

This repository provides **baseline architectural defaults**, defensive templates, and sanity checks for early-stage software development. It does **not** provide a formal guarantee of security, legal compliance, or vulnerability-free operation. Users and developers must review all LLM output and generated code before deploying to production environments.

