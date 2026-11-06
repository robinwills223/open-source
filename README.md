# Open Source

An open-source architectural guide and deterministic scaffolding engine guiding non-technical founders, junior developers, and senior developers from an idea to a tested, deployable product using an LLM as the interface.

---

## Getting Started: Repo Foundation

All core architectural documents, schemas, tooling, project templates, and tests are organized inside [`repo-foundation/`](repo-foundation/):

- **[Repo Foundation README](repo-foundation/README.md):** Vision, audience overview, quick-start commands, and architectural policies.
- **[Architectural Rules & Triggers (`docs/05`)](repo-foundation/docs/05-rules-single-source.md):** The sole authoritative source for scope derivation, triggers, and safeguards.
- **[Profile Schema](repo-foundation/schemas/project.profile.schema.json):** Formal JSON Schema specification.
- **[Reference Tooling & Project Generator](repo-foundation/tools/):** Profile validation CLI, link checker, hygiene scanner, and Django small-tool project generator.
- **[Beginner Guide: Run Locally](repo-foundation/docs/guides/run-locally.md):** Step-by-step instructions for running the generated application locally.
- **[Guide: What You Get](repo-foundation/docs/guides/what-you-get.md):** Overview of the starter records tracker workflow and baseline security limits.
- **[Guide: Minimum Viable Backup & Restore](repo-foundation/docs/guides/backup-and-restore.md):** Native SQLite snapshots, off-server synchronization, and restore verification drills.
- **[Guide: Baseline Security Audit](repo-foundation/docs/guides/security-baseline.md):** Pre-launch sanity checks and dependency auditing procedures (`pip-audit`).
- **[Guide: Single-Node VPS Deployment](repo-foundation/docs/guides/deploy.md):** Step-by-step Ubuntu + systemd + Caddy production deployment guide.
- **[Launch Checklist](repo-foundation/docs/guides/launch-checklist.md):** Printable go-live and operational maintenance checklist.
- **[Customer Validation Kit](repo-foundation/docs/validation/01-before-you-build.md):** Customer interviews, demand testing, and pilot cohort management frameworks.
