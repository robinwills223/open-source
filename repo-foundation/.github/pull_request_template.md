## Description
Briefly describe the change and its rationale.

## Pre-Merge Checklist
- [ ] **Tests Pass:** All unit, boundary, schema, and fixture tests pass (`python -m pytest`).
- [ ] **Link & Hygiene Checks Pass:** `python tools/check_links.py` and `python tools/check_repo_hygiene.py` exit with 0.
- [ ] **Single Source of Truth Rule:** If architectural rules, triggers, or thresholds changed, they were updated in **all three places simultaneously**:
  - `docs/05-rules-single-source.md`
  - `tools/rules.py`
  - `tests/test_rules.py`
- [ ] **No Secrets or Personal Paths:** Confirmed no API keys, private tokens, passwords, personal user directories, or personal names were committed.
- [ ] **Decision Logged:** Any new architectural judgment call or rejected alternative is documented in `docs/DECISIONS.md`.
