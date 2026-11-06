"""Project generator for repo-foundation (v0.1.0-alpha).

Generates a local Django small-tool project from a validated profile.
Usage: python tools/generate_project.py <profile.yaml> <output_dir>
Exit codes:
  0: Successfully generated
  1: Invalid profile or non-empty output directory
  2: Blocked/halted profile, or profile outside v0.1 support scope
"""

import shutil
import sys
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.rules import derive_scope
from tools.validate_profile import validate_file

TEMPLATE_DIR = REPO_ROOT / "templates" / "django-small-tool"


def build_decisions_for_founder(profile: dict) -> str:
    """Generate DECISIONS-FOR-FOUNDER.md tailored to audience persona."""
    name = profile.get("name", "my-tool")
    audience = profile.get("audience", "non_technical_founder")
    caps = profile.get("capabilities", {})
    mvb = caps.get("minimum_viable_backup", False)

    if audience == "senior_developer":
        lines = [
            f"# Architectural Decisions: {name}",
            "",
            "## Baseline Profile Evaluation",
            f"- **Stack:** Django (pinned LTS 5.2.9)",
            f"- **Shape:** small_tool (monolithic synchronous)",
            f"- **Scope:** small (SQLite default, single-node execution)",
            "- **Active Capabilities:** None (all heavy infrastructure OFF by default)",
            "",
            "## Capability States",
            "- `docker`: OFF (solo local execution)",
            "- `postgres`: OFF (SQLite adequate for <500 user band)",
            "- `redis` & `background_jobs`: OFF (no asynchronous task signals)",
            "- `ci`: OFF (single-developer repository)",
            "- `error_monitoring` & `backups`: OFF (medium-tier infrastructure)",
        ]
        if mvb:
            lines.extend(
                [
                    "",
                    "## Operational Notice: Backup Routine Required",
                    "> [!IMPORTANT]",
                    "> `minimum_viable_backup` is active based on validation stage. Automated backup scripts are not included in v0.1; establish an external off-host database snapshot before onboarding production users.",
                ]
            )
        lines.extend(
            [
                "",
                "## Next Steps",
                "1. `python -m venv .venv && source .venv/bin/activate`",
                "2. `pip install -r requirements.txt`",
                "3. `cp .env.example .env`",
                "4. `python manage.py migrate`",
                "5. `python manage.py test`",
            ]
        )
        return "\n".join(lines) + "\n"

    elif audience == "junior_developer":
        lines = [
            f"# Architecture & Design Summary: {name}",
            "",
            "Welcome! Your project has been scaffolded using clean Django architectural defaults.",
            "",
            "## Why Capabilities are OFF by Default",
            "- **No Docker:** You are working locally. Container overhead is unnecessary until multiple developers collaborate.",
            "- **SQLite Instead of PostgreSQL:** SQLite is fast, zero-configuration, and reliable for up to hundreds of users.",
            "- **No Redis or Celery:** Asynchronous queues add moving parts and hosting costs; keep tasks synchronous until API timeouts measure a need.",
            "- **No CI Pipelines:** Set up pull-request automation when a second contributor begins submitting code.",
        ]
        if mvb:
            lines.extend(
                [
                    "",
                    "## Backup Advisory",
                    "> [!WARNING]",
                    "> Because your product has active or beta users, data protection is essential. v0.1 does not yet ship an automated backup runner. Please set up a scheduled SQLite `.backup` routine before live launch.",
                ]
            )
        lines.extend(
            [
                "",
                "## Getting Started",
                "1. Follow the local run guide in `README.md`.",
                "2. Run automated tests with `python manage.py test`.",
                "3. Use Django admin to manage records and users.",
            ]
        )
        return "\n".join(lines) + "\n"

    else:
        # Non-technical founder
        lines = [
            f"# Plain-Language Guide for {name}",
            "",
            "Congratulations! Your new software starter is ready to run on your computer.",
            "",
            "## What Was Built for You",
            f"We created a secure, focused starter application called **{name}**. It includes:",
            "- A personal workspace where you can create, edit, view, and delete records.",
            "- Private account protection so each user only sees their own information.",
            "- A safe download button to export your records to a spreadsheet anytime.",
            "",
            "## Why Extra Tools are Turned OFF",
            "We purposely kept this project simple and free to run:",
            "- **No expensive cloud databases:** It runs on a lightweight local database on your computer.",
            "- **No complicated background servers:** Everything runs simply and fast in a single program.",
            "- **No extra hosting bills:** You can test your idea for $0 right now.",
        ]
        if mvb:
            lines.extend(
                [
                    "",
                    "## Important Notice About Backups",
                    "> [!IMPORTANT]",
                    "> **Save your data regularly:** Because your project is reaching real users, you will need a backup copy of your database. In this early preview (v0.1), automated backup scripts are not yet built-in. Make sure you copy your `db.sqlite3` file to a safe place before real customer data arrives.",
                ]
            )
        lines.extend(
            [
                "",
                "## What You Should Do Next",
                "1. Open this folder in your LLM tool.",
                "2. Say: *\"Walk me through running my new app step by step.\"*",
                "3. Follow the instructions to start the server and see your app in your browser!",
            ]
        )
        return "\n".join(lines) + "\n"


def generate_project(profile_path: Path, output_dir: Path) -> int:
    """Validate profile, enforce v0.1 support scope, and scaffold Django project."""
    # 1. Validation (must pass schema, triggers, and safeguards)
    code, findings, data = validate_file(profile_path)
    if code != 0:
        print(f"Generation aborted: profile validation returned exit code {code}.")
        for f in findings:
            print(f"  [{f.type}] {f.message}")
        return code

    assert data is not None

    # 2. Enforce v0.1 Support Scope
    scope = derive_scope(data)
    shape = data.get("product_shape")
    stack = data.get("stack")
    caps = data.get("capabilities", {})

    # Disallow capabilities other than minimum_viable_backup in v0.1
    unsupported_caps = [
        cap
        for cap, active in caps.items()
        if active and cap != "minimum_viable_backup"
    ]

    if stack != "django" or shape != "small_tool" or scope != "small" or unsupported_caps:
        reasons = []
        if stack != "django":
            reasons.append(f"stack '{stack}' (v0.1 supports 'django' only)")
        if shape != "small_tool":
            reasons.append(f"product_shape '{shape}' (v0.1 supports 'small_tool' only)")
        if scope != "small":
            reasons.append(f"derived scope '{scope}' (v0.1 supports 'small' scope only)")
        if unsupported_caps:
            reasons.append(f"active capabilities {unsupported_caps} (v0.1 supports zero optional capabilities)")

        print("Generation halted: Profile is outside v0.1 alpha support scope.")
        print("Reasons:")
        for r in reasons:
            print(f"  - {r}")
        print("Automated scaffolding for medium/enterprise architectures and optional capabilities will be added in future releases.")
        return 2

    # 3. Check output directory
    output_path = output_dir.resolve()
    if output_path.exists() and any(output_path.iterdir()):
        print(f"Error: Output directory '{output_path}' exists and is not empty. Refusing to overwrite.")
        return 1

    # 4. Copy template
    if not TEMPLATE_DIR.is_dir():
        print(f"Error: Template directory '{TEMPLATE_DIR}' not found.")
        return 1

    output_path.mkdir(parents=True, exist_ok=True)
    for item in TEMPLATE_DIR.iterdir():
        dest = output_path / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)

    # 5. Substitute project name in README.md
    project_name = data.get("name", "my-tool")
    readme_path = output_path / "README.md"
    if readme_path.is_file():
        content = readme_path.read_text(encoding="utf-8")
        content = content.replace("My Small Tool Starter", f"{project_name.replace('-', ' ').title()}")
        readme_path.write_text(content, encoding="utf-8")

    # 5b. Initialize .env from .env.example if not present
    env_example = output_path / ".env.example"
    env_target = output_path / ".env"
    if env_example.is_file() and not env_target.exists():
        shutil.copy2(env_example, env_target)

    # 6. Copy profile into output
    shutil.copy2(profile_path, output_path / "project.profile.yaml")

    # 7. Write DECISIONS-FOR-FOUNDER.md
    decisions_content = build_decisions_for_founder(data)
    (output_path / "DECISIONS-FOR-FOUNDER.md").write_text(decisions_content, encoding="utf-8")

    print(f"SUCCESS: Generated project '{project_name}' in {output_path}")
    print(f"Next step: Follow instructions in {output_path / 'README.md'} to start your app.")
    return 0


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python tools/generate_project.py <path/to/profile.yaml> <output_dir>")
        return 1

    profile_file = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    return generate_project(profile_file, out_dir)


if __name__ == "__main__":
    sys.exit(main())
