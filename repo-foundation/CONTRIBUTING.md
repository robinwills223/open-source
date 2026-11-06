# Contributing to Repo Foundation

Thank you for contributing! This project is maintained by volunteers with **best-effort response times**. Please follow these principles and guidelines.

---

## Strict Rule Modification Policy

`docs/05-rules-single-source.md` and `tools/rules.py` are the single source of truth for architectural derivations, capability triggers, and safeguards:

> [!IMPORTANT]
> **Single-Commit Rule Synchronization:** Any proposed change to intake derivation, triggers, or boundaries must update **all three** in the same pull request:
> 1. The authoritative prose in `docs/05-rules-single-source.md`.
> 2. The executable pure functions in `tools/rules.py`.
> 3. Corresponding unit and table-driven tests in `tests/test_rules.py`.

Never modify rule behavior in `tools/rules.py` without updating `docs/05`, and never alter rules in `docs/05` without updating `tools/rules.py` and test cases.

---

## Running the Tests

Install dev dependencies and run the complete test suite:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -v
python tools/check_links.py
python tools/check_repo_hygiene.py
```

All tests, link checks, and hygiene checks must pass before opening a pull request.

---

## Proposing a New Example Profile

To add an example project profile:
1. Place valid profiles in `examples/profiles/valid/<project-name>.yaml`.
2. Place invalid or rejection fixtures in `examples/profiles/invalid/<project-name>.yaml`. Every invalid profile must include an `# EXPECTED_FAILURE: <substring>` comment on line 1 describing the expected failure reason.
3. Run `pytest tests/test_fixtures.py` to confirm that all fixtures pass their automated expectations.

---

## Logging Decisions

Every design trade-off, rejected alternative, or judgment call must be documented in `docs/DECISIONS.md` under an incremental `DEC-XXX` identifier. Pull requests that introduce new architectural assumptions without a corresponding decision record will be requested to document them.

---

## Submitting Bug Reports

A good bug report includes:
- Your LLM interface or tool and exact version (if applicable).
- Your user audience tier (`non_technical_founder`, `junior_developer`, or `senior_developer`).
- The full terminal output or error trace.
- A minimal reproducible `project.profile.yaml` (sanitize any private business secrets).
- Expected vs. actual behavior.

