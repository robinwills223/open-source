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
