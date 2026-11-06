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
- Minimum viable backup and restore management commands (`backup_db`, `verify_backup`) with streaming SQLite snapshots, integrity checks, and retention pruning.
- Minimum viable backup guide (`docs/guides/backup-and-restore.md`) covering cron automation, rclone off-server synchronization, and restore verification drills.
- Pre-launch baseline security audit command (`baseline_check`) evaluating DEBUG mode, SECRET_KEY length, ALLOWED_HOSTS, gitignore, and web static/media isolation.
- Operational baseline security guide (`docs/guides/security-baseline.md`) including PyPA `pip-audit` dependency vulnerability auditing procedures.
- Production deployment dependencies (`requirements-deploy.txt`) with exact pinned versions of `gunicorn==23.0.0` and `whitenoise==6.9.0`.
- Single-node Ubuntu VPS deployment guide (`docs/guides/deploy.md`) with systemd process supervision and Caddy automatic HTTPS.
- Pre-launch and operational maintenance checklist (`docs/guides/launch-checklist.md`).
- Customer validation kit (`docs/validation/01-04`) with frameworks for problem validation, Mom Test interview scripts, demand landing page metrics, and pilot cohort operation.
- Reusable validation templates (`templates/validation/interview-notes.md`, `templates/validation/pilot-tracker.csv`).
- Cold-start usability test protocol (`docs/testing/cold-start-test.md`).
- Public repository community files (`README.md`, `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`, issue templates, PR template).

