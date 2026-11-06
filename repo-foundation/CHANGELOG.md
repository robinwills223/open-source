# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

- Additional framework stack adapters (FastAPI, Node.js, Next.js).
- Medium and Enterprise scope automated scaffolding recipes.
- Cloud hosting deployment recipes and automation scripts.
- Automated backup sync worker implementation.

---

## [0.1.0-alpha] - Planned

### Added
- Authoritative architectural specification documents (`docs/00` through `docs/05`).
- Formal JSON Schema (`schemas/project.profile.schema.json`) defining profile structure and conditional safety invariants.
- Executable rule reference implementation (`tools/rules.py`) with highest-signal-wins scope derivation and capability trigger logic.
- Profile validation CLI tool (`tools/validate_profile.py`) with exit codes (0 = valid, 1 = invalid, 2 = halted/blocked).
- GitHub markdown link and heading-slug anchor verifier (`tools/check_links.py`).
- Repository hygiene and secret detection tool (`tools/check_repo_hygiene.py`).
- 8 valid and 5 invalid profile fixture examples (`examples/profiles/`).
- Full pytest test suite covering boundary cases, triggers, schema invariants, overrides, and fixtures.
- Working Django small-tool project template (`templates/django-small-tool/`) with login, ownership isolation, CSV export formula-injection protection, and local test suite.
- Project generator CLI tool (`tools/generate_project.py`) with tailored `DECISIONS-FOR-FOUNDER.md` generator.
- Step-by-step beginner guides (`docs/guides/run-locally.md`, `docs/guides/what-you-get.md`).
- Cold-start usability test protocol (`docs/testing/cold-start-test.md`).
- Public repository community files (`README.md`, `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, issue templates, PR template).

