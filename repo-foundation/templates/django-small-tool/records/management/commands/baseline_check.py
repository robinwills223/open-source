"""Management command to evaluate operational security baseline before launch.

Cites: docs/05 Section 8 (Operational Safeguards).
Uses Python standard library and Django core APIs only.
Reports status as PASS, WARN, or FAIL with plain-language explanations.
Never displays secret values in output.
"""

import io
import os
from pathlib import Path
import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Evaluates the baseline security configuration and prints a plain-language readiness report."

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Treat all warnings as failures (useful for pre-deploy CI checks).",
        )

    def handle(self, *args, **options):
        strict = options.get("strict", False)
        findings = []  # list of tuples: (status, title, why, fix)

        self.stdout.write("=" * 60)
        self.stdout.write("BASELINE SECURITY AUDIT")
        self.stdout.write("=" * 60)

        # Check 1: DEBUG setting
        is_prod = os.environ.get("DJANGO_ENV", "").lower() == "production" or os.environ.get("ENVIRONMENT", "").lower() == "production"
        if settings.DEBUG and is_prod:
            findings.append((
                "FAIL",
                "DEBUG mode is ON in production",
                "Leaving DEBUG on reveals detailed code and configuration details whenever an error occurs.",
                "Set DEBUG=False in your production environment variables (.env).",
            ))
        elif settings.DEBUG:
            findings.append((
                "WARN",
                "DEBUG mode is ON (Development mode)",
                "DEBUG is helpful while building on your computer, but must be turned OFF before real users access the app.",
                "Keep DEBUG=True locally; ensure DEBUG=False is set on your live server.",
            ))
        else:
            findings.append((
                "PASS",
                "DEBUG mode is OFF",
                "Detailed internal error screens are hidden from visitors.",
                "None needed.",
            ))

        # Check 2: SECRET_KEY
        secret_key = getattr(settings, "SECRET_KEY", "") or ""
        key_len = len(secret_key)
        has_insecure_prefix = secret_key.startswith("django-insecure-") or "insecure" in secret_key.lower()
        if not secret_key or key_len < 50 or has_insecure_prefix:
            findings.append((
                "FAIL",
                f"SECRET_KEY is inadequate (length: {key_len} characters)",
                "Django uses this secret string to protect login sessions, reset tokens, and cookies against tampering.",
                "Generate a random string of 50+ characters and set SECRET_KEY in your production .env file.",
            ))
        else:
            findings.append((
                "PASS",
                f"SECRET_KEY is configured with adequate length ({key_len} characters)",
                "Session cookies and security tokens are cryptographically protected.",
                "None needed.",
            ))

        # Check 3: ALLOWED_HOSTS
        allowed = getattr(settings, "ALLOWED_HOSTS", [])
        if not allowed or "*" in allowed:
            findings.append((
                "FAIL",
                "ALLOWED_HOSTS is empty or contains wildcard '*'",
                "Without host validation, attackers can forge Host headers to compromise password-reset links and cache poisoning.",
                "Set ALLOWED_HOSTS in .env to your specific domain names (e.g. ALLOWED_HOSTS=myapp.com,www.myapp.com).",
            ))
        elif not settings.DEBUG and allowed == ["127.0.0.1", "localhost", "testserver"]:
            findings.append((
                "WARN",
                "ALLOWED_HOSTS contains only local addresses while DEBUG is OFF",
                "Your application will reject web traffic that arrives with your public domain name.",
                "Add your real public domain to ALLOWED_HOSTS in .env before directing live traffic.",
            ))
        else:
            findings.append((
                "PASS",
                f"ALLOWED_HOSTS restricted to {len(allowed)} domain(s)",
                "Requests with unrecognized or spoofed domains will be safely blocked.",
                "None needed.",
            ))

        # Check 4: .env file ignored by git
        gitignore_path = Path(settings.BASE_DIR) / ".gitignore"
        env_ignored = False
        if gitignore_path.is_file():
            content = gitignore_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                stripped = line.strip()
                if stripped in [".env", "*.env", ".env*", ".env.local"]:
                    env_ignored = True
                    break
        if not env_ignored:
            findings.append((
                "FAIL",
                ".env file is not ignored in .gitignore",
                "If .env is tracked in git, private passwords, database keys, and secrets can leak to public or shared repositories.",
                "Add '.env' on a new line in your project's .gitignore file immediately.",
            ))
        else:
            findings.append((
                "PASS",
                ".env file is ignored in .gitignore",
                "Local environment files containing secrets will not be committed to source control.",
                "None needed.",
            ))

        # Check 5: Django's built-in check --deploy
        deploy_stdout = io.StringIO()
        deploy_stderr = io.StringIO()
        try:
            call_command("check", "--deploy", stdout=deploy_stdout, stderr=deploy_stderr)
            check_output = deploy_stdout.getvalue() + deploy_stderr.getvalue()
            # Count warnings from check --deploy
            lines = [l for l in check_output.splitlines() if "(security." in l]
            if lines:
                findings.append((
                    "WARN",
                    f"Django deployment checks identified {len(lines)} recommendation(s)",
                    "Django has standard built-in deployment recommendations (e.g. HTTPS headers, session cookies).",
                    "Review 'python manage.py check --deploy' and configure HTTPS headers in production.",
                ))
            else:
                findings.append((
                    "PASS",
                    "Django deployment checks reported zero critical security issues",
                    "Baseline Django deployment validations completed cleanly.",
                    "None needed.",
                ))
        except Exception as exc:
            findings.append((
                "WARN",
                f"Deployment check runner encountered an advisory: {exc}",
                "Automated check tool could not complete all deployment inspections.",
                "Run 'python manage.py check --deploy' manually to view recommendations.",
            ))

        # Check 6: Database and backup directory not in public static/media roots
        db_conf = settings.DATABASES.get("default", {})
        db_name = str(db_conf.get("NAME", ""))
        db_path = Path(db_name).resolve() if db_name and not (":memory:" in db_name or "mode=memory" in db_name) else None
        backup_dir = Path(os.environ.get("BACKUP_DIR") or (settings.BASE_DIR / "backups")).resolve()

        static_root = Path(settings.STATIC_ROOT).resolve() if getattr(settings, "STATIC_ROOT", None) else None
        media_root = Path(settings.MEDIA_ROOT).resolve() if getattr(settings, "MEDIA_ROOT", None) else None
        static_dirs = [Path(d).resolve() for d in getattr(settings, "STATICFILES_DIRS", [])]

        forbidden_dirs = [d for d in [static_root, media_root] + static_dirs if d is not None]

        def is_subpath(child: Path, parent: Path) -> bool:
            try:
                child.relative_to(parent)
                return True
            except ValueError:
                return False

        exposed = []
        for pub_dir in forbidden_dirs:
            if db_path and is_subpath(db_path, pub_dir):
                exposed.append(f"Database file ({db_path.name}) is inside public directory: {pub_dir}")
            if is_subpath(backup_dir, pub_dir):
                exposed.append(f"Backup directory ({backup_dir.name}) is inside public directory: {pub_dir}")

        if exposed:
            findings.append((
                "FAIL",
                "Database or backup files are located inside publicly served media/static directories",
                "Files located in web static or media folders can be downloaded directly by anyone over the internet.",
                "Relocate the database and backups outside public folders (e.g. into the project root or a persistent data volume).",
            ))
        else:
            findings.append((
                "PASS",
                "Database and backup directories are isolated from public static/media trees",
                "Data files cannot be browsed or downloaded by external web visitors.",
                "None needed.",
            ))

        # Check 7: Staff and admin accounts
        try:
            User = get_user_model()
            staff_users = User.objects.filter(is_staff=True)
            problem_staff = []
            for u in staff_users:
                if not u.has_usable_password():
                    problem_staff.append(f"User '{u.username}' has an unusable password.")
                if not u.email:
                    problem_staff.append(f"User '{u.username}' has no recovery email address.")
            if problem_staff:
                findings.append((
                    "WARN",
                    f"Staff account audit flagged {len(problem_staff)} account advisory items",
                    "Administrative accounts should have strong passwords and active emails for recovery and auditability.",
                    "Log into Django admin (/admin/) and ensure staff accounts have valid emails and passwords.",
                ))
            else:
                findings.append((
                    "PASS",
                    f"Staff account review clean ({staff_users.count()} staff accounts evaluated)",
                    "Administrator accounts meet baseline credential requirements.",
                    "None needed.",
                ))
        except Exception:
            # Database might not be migrated yet or table not ready
            findings.append((
                "WARN",
                "User table could not be audited (database not migrated)",
                "Cannot inspect administrator accounts until database migrations are run.",
                "Run 'python manage.py migrate' then re-run baseline_check.",
            ))

        # Render formatted plain-language report
        has_fail = False
        has_warn = False

        for status, title, why, fix in findings:
            if status == "FAIL":
                has_fail = True
                badge = self.style.ERROR("[FAIL]")
            elif status == "WARN":
                has_warn = True
                badge = self.style.WARNING("[WARN]")
            else:
                badge = self.style.SUCCESS("[PASS]")

            self.stdout.write(f"\n{badge} {title}")
            self.stdout.write(f"  Why it matters: {why}")
            if status != "PASS":
                self.stdout.write(f"  How to fix:     {fix}")

        self.stdout.write("\n" + "=" * 60)
        if has_fail or (strict and has_warn):
            self.stdout.write(self.style.ERROR("AUDIT RESULT: FAIL. Baseline security issues must be resolved before launch."))
            self.stdout.write("=" * 60)
            raise CommandError("Baseline security check failed. See recommendations above.")
        elif has_warn:
            self.stdout.write(self.style.WARNING("AUDIT RESULT: PASS WITH WARNINGS. Ready for development; review warnings before production."))
            self.stdout.write("=" * 60)
        else:
            self.stdout.write(self.style.SUCCESS("AUDIT RESULT: ALL PASS. Baseline security requirements satisfied."))
            self.stdout.write("=" * 60)
