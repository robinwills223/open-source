# Vision & Core Philosophy

## Purpose
This repository provides a tool-agnostic, LLM-guided pathway that takes non-technical founders, junior developers, and senior developers from an initial concept to a validated, tested software product.

Instead of presenting an intimidating boilerplate filled with enterprise infrastructure, this repository treats complexity as something that must be earned. An LLM acts as the interactive architect, asking targeted questions and generating only the exact code, configuration, and documentation needed for the user's specific stage.

## Who It Is For
- **Non-Technical Founders:** Entrepreneurs with domain expertise who need working software to test demand or serve initial users without being overwhelmed by technical jargon, cloud bills, or DevOps maintenance.
- **Junior Developers:** Builders looking for clear structure, sensible defaults, and best-practice guidance without getting lost in microservices, complex build pipelines, or prematurely optimized architectures.
- **Senior Developers:** Experienced engineers who want an autonomous, opinionated scaffolding assistant that respects clean design, minimizes repetitive setup, and steps aside when custom overrides are required.

## What It Is NOT
To maintain integrity and trust, the boundaries of this repository are strictly defined:
- **NOT a No-Code Website Builder:** It does not provide drag-and-drop visual canvases or proprietary walled gardens. It designs and scaffolds real, clean code that the user owns completely.
- **NOT a Security or Compliance Guarantee:** It provides solid **baseline** architectural conventions (such as environment variable isolation and default password hashing). It does **not** make a product inherently "secure," "unhackable," or "compliant" with regulations (HIPAA, GDPR, PCI-DSS). True security requires continuous auditing, operational vigilance, and specialized verification.
- **NOT a Replacement for Legal, Financial, or Medical Advice:** Automated scaffolding cannot evaluate regulatory exposure, draft terms of service, or ensure compliance with localized legal mandates.
- **NOT an Unchecked Autonomous Generator:** It does not introduce third-party services, dependencies, or infrastructure layers without an explicit trigger and recorded explanation from the project profile.

## The Core Principle: Zero-Debt Progressive Disclosure
Every capability (Docker, Redis, background task queues, external databases, rate limiting, and compliance workflows) is **OFF by default**. 

A small project or early demand test will never see enterprise tooling. Complexity unlocks only when a project's verified profile provides a concrete, undeniable requirement. If SQLite and a single-process server solve the problem, that is where the project begins.

