"""Automated tests for records tracker starter app.

Covers:
- Model behavior and timestamps
- Strict login enforcement on all views
- Cross-user ownership isolation (returns 404 on unowned records)
- Spreadsheet formula injection protection in CSV exports
- Status filtering
- Production settings behavior and manage.py check --deploy
"""

import hashlib
import io
import os
import sqlite3
import tempfile
from pathlib import Path
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command, CommandError
from django.test import TestCase, SimpleTestCase, override_settings
from django.urls import reverse
from .models import Record
from .views import sanitize_csv_cell


class RecordModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="secretpassword123")

    def test_record_creation_and_str(self):
        record = Record.objects.create(user=self.user, title="Inventory Audit", notes="Quarterly review", status="active")
        self.assertEqual(str(record), "Inventory Audit")
        self.assertEqual(record.status, "active")
        self.assertIsNotNone(record.created_at)
        self.assertIsNotNone(record.updated_at)


class RecordViewAccessTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="secretpassword123")
        self.bob = User.objects.create_user(username="bob", password="secretpassword123")
        self.alice_record = Record.objects.create(user=self.alice, title="Alice Secret Project", status="active")

    def test_unauthenticated_requests_redirect_to_login(self):
        urls = [
            reverse("records:record_list"),
            reverse("records:record_create"),
            reverse("records:record_detail", kwargs={"pk": self.alice_record.pk}),
            reverse("records:record_update", kwargs={"pk": self.alice_record.pk}),
            reverse("records:record_delete", kwargs={"pk": self.alice_record.pk}),
            reverse("records:record_export_csv"),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302, f"{url} should redirect unauthenticated request")
            self.assertIn("/accounts/login/", response.url)

    def test_ownership_isolation_on_detail_view(self):
        # Bob cannot view Alice's record -> returns 404
        self.client.login(username="bob", password="secretpassword123")
        response = self.client.get(reverse("records:record_detail", kwargs={"pk": self.alice_record.pk}))
        self.assertEqual(response.status_code, 404)

        # Alice CAN view her own record -> returns 200
        self.client.login(username="alice", password="secretpassword123")
        response = self.client.get(reverse("records:record_detail", kwargs={"pk": self.alice_record.pk}))
        self.assertEqual(response.status_code, 200)

    def test_ownership_isolation_on_edit_view(self):
        # Bob cannot edit Alice's record -> returns 404
        self.client.login(username="bob", password="secretpassword123")
        response = self.client.post(
            reverse("records:record_update", kwargs={"pk": self.alice_record.pk}),
            {"title": "Hacked Title", "status": "active", "notes": ""},
        )
        self.assertEqual(response.status_code, 404)
        self.alice_record.refresh_from_db()
        self.assertEqual(self.alice_record.title, "Alice Secret Project")

    def test_ownership_isolation_on_delete_view(self):
        # Bob cannot delete Alice's record -> returns 404
        self.client.login(username="bob", password="secretpassword123")
        response = self.client.post(reverse("records:record_delete", kwargs={"pk": self.alice_record.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Record.objects.filter(pk=self.alice_record.pk).exists())

    def test_status_filter_on_list_view(self):
        self.client.login(username="alice", password="secretpassword123")
        Record.objects.create(user=self.alice, title="Draft Item", status="draft")
        Record.objects.create(user=self.alice, title="Archived Item", status="archived")

        # Filter by active
        res_active = self.client.get(reverse("records:record_list") + "?status=active")
        self.assertEqual(res_active.status_code, 200)
        self.assertContains(res_active, "Alice Secret Project")
        self.assertNotContains(res_active, "Draft Item")

        # Filter by draft
        res_draft = self.client.get(reverse("records:record_list") + "?status=draft")
        self.assertContains(res_draft, "Draft Item")
        self.assertNotContains(res_draft, "Alice Secret Project")


class CsvExportTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="secretpassword123")
        self.bob = User.objects.create_user(username="bob", password="secretpassword123")
        # Alice creates a record with formula injection payload
        Record.objects.create(user=self.alice, title="=SUM(A1:A10)", notes="+cmd|' /C calc'!A0", status="active")
        Record.objects.create(user=self.bob, title="Bob Secret", notes="Confidential", status="active")

    def test_csv_export_ownership_and_sanitization(self):
        self.client.login(username="alice", password="secretpassword123")
        response = self.client.get(reverse("records:record_export_csv"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")

        content = response.content.decode("utf-8")
        # Alice's formula payloads must be sanitized with leading single quote
        self.assertIn("'=SUM(A1:A10)", content)
        self.assertIn("'+cmd|' /C calc'!A0", content)
        # Bob's records must NOT be present
        self.assertNotIn("Bob Secret", content)

    def test_sanitize_csv_cell_helper(self):
        self.assertEqual(sanitize_csv_cell("=1+1"), "'=1+1")
        self.assertEqual(sanitize_csv_cell("+2+2"), "'+2+2")
        self.assertEqual(sanitize_csv_cell("-3-3"), "'-3-3")
        self.assertEqual(sanitize_csv_cell("@SUM(1)"), "'@SUM(1)")
        self.assertEqual(sanitize_csv_cell("Normal Text"), "Normal Text")
        self.assertEqual(sanitize_csv_cell(""), "")
        self.assertEqual(sanitize_csv_cell(None), "")


class DeploymentCheckTests(TestCase):
    @override_settings(
        DEBUG=False,
        SECRET_KEY="test-production-secret-key-that-is-sufficiently-long-and-random",
        ALLOWED_HOSTS=["example.com"],
        SECURE_SSL_REDIRECT=True,
        SESSION_COOKIE_SECURE=True,
        CSRF_COOKIE_SECURE=True,
        SECURE_BROWSER_XSS_FILTER=True,
        SECURE_CONTENT_TYPE_NOSNIFF=True,
        X_FRAME_OPTIONS="DENY",
        SECURE_HSTS_SECONDS=31536000,
        SECURE_HSTS_INCLUDE_SUBDOMAINS=True,
        SECURE_HSTS_PRELOAD=True,
    )
    def test_check_deploy_command(self):
        out = io.StringIO()
        call_command("check", "--deploy", stdout=out)
        output = out.getvalue()
        # Ensure system checks pass without fatal errors
        self.assertNotIn("SystemCheckError", output)


class BackupAndRestoreTests(SimpleTestCase):
    def setUp(self):
        self.tmp_dir_obj = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir_obj.name)
        self.live_db = self.tmp_path / "live.sqlite3"
        conn = sqlite3.connect(str(self.live_db))
        conn.execute("CREATE TABLE records_record (id INTEGER PRIMARY KEY, title TEXT, status TEXT);")
        for i in range(10):
            conn.execute("INSERT INTO records_record (title, status) VALUES (?, ?);", (f"Record {i}", "active"))
        conn.commit()
        conn.close()

    def tearDown(self):
        try:
            self.tmp_dir_obj.cleanup()
        except Exception:
            pass

    def test_backup_db_creation_and_consistency(self):
        backup_dir = self.tmp_path / "backups"
        out = io.StringIO()

        # Simulate concurrent writer connection
        writer_conn = sqlite3.connect(str(self.live_db))
        writer_conn.execute("INSERT INTO records_record (title, status) VALUES ('Concurrent item', 'active');")
        writer_conn.commit()

        call_command("backup_db", source=str(self.live_db), backup_dir=str(backup_dir), keep=5, stdout=out)
        writer_conn.close()

        output = out.getvalue()
        self.assertIn("PASS: Backup created successfully", output)

        backup_files = list(backup_dir.glob("backup_*.sqlite3"))
        self.assertEqual(len(backup_files), 1)

        # Integrity check on the backup file
        chk_conn = sqlite3.connect(str(backup_files[0]))
        cursor = chk_conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        self.assertEqual(cursor.fetchall(), [("ok",)])
        chk_conn.close()

    def test_verify_backup_catches_corrupted_file(self):
        backup_dir = self.tmp_path / "backups"
        call_command("backup_db", source=str(self.live_db), backup_dir=str(backup_dir), stdout=io.StringIO())
        backup_files = list(backup_dir.glob("backup_*.sqlite3"))
        self.assertTrue(len(backup_files) >= 1)
        corrupt_file = backup_files[0]

        # Intentionally corrupt header bytes
        with open(corrupt_file, "r+b") as f:
            f.seek(16)
            f.write(b"\x00" * 32)

        with self.assertRaises(CommandError):
            call_command("verify_backup", str(corrupt_file), stdout=io.StringIO())

    def test_backup_retention_policy(self):
        backup_dir = self.tmp_path / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        # Create 5 dummy backup files with staggered timestamps
        for i in range(5):
            f = backup_dir / f"backup_2026010{i}_120000.sqlite3"
            f.write_text("dummy", encoding="utf-8")

        # Run backup with keep=3
        call_command("backup_db", source=str(self.live_db), backup_dir=str(backup_dir), keep=3, stdout=io.StringIO())
        remaining = list(backup_dir.glob("backup_*.sqlite3"))
        self.assertEqual(len(remaining), 3)

    def test_verify_backup_never_modifies_live_db(self):
        def get_checksum(p):
            with open(p, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()

        initial_checksum = get_checksum(self.live_db)
        backup_dir = self.tmp_path / "backups"

        call_command("backup_db", source=str(self.live_db), backup_dir=str(backup_dir), stdout=io.StringIO())
        backup_files = list(backup_dir.glob("backup_*.sqlite3"))
        self.assertEqual(len(backup_files), 1)

        out = io.StringIO()
        call_command("verify_backup", str(backup_files[0]), stdout=out)
        self.assertIn("PASS: Backup verification completed successfully", out.getvalue())

        final_checksum = get_checksum(self.live_db)
        self.assertEqual(initial_checksum, final_checksum)

    def test_verify_backup_completes_and_reports_elapsed_time(self):
        backup_dir = self.tmp_path / "backups"
        call_command("backup_db", source=str(self.live_db), backup_dir=str(backup_dir), stdout=io.StringIO())
        backup_files = list(backup_dir.glob("backup_*.sqlite3"))
        self.assertEqual(len(backup_files), 1)

        out = io.StringIO()
        call_command("verify_backup", str(backup_files[0]), stdout=out)
        output = out.getvalue()

        self.assertIn("Elapsed time:", output)
        self.assertIn("records_record", output)
        self.assertIn("Total rows verified across all tables:", output)


class BaselineCheckTests(SimpleTestCase):
    def test_baseline_check_passing_conditions(self):
        good_key = "a" * 55
        with override_settings(DEBUG=False, SECRET_KEY=good_key, ALLOWED_HOSTS=["example.com"]):
            out = io.StringIO()
            call_command("baseline_check", stdout=out)
            output = out.getvalue()
            self.assertIn("AUDIT RESULT:", output)
            self.assertNotIn(good_key, output)

    def test_baseline_check_debug_true_in_production_fails(self):
        good_key = "b" * 55
        with override_settings(DEBUG=True, SECRET_KEY=good_key):
            old_env = os.environ.get("DJANGO_ENV")
            os.environ["DJANGO_ENV"] = "production"
            try:
                with self.assertRaises(CommandError):
                    call_command("baseline_check", stdout=io.StringIO())
            finally:
                if old_env is None:
                    os.environ.pop("DJANGO_ENV", None)
                else:
                    os.environ["DJANGO_ENV"] = old_env

    def test_baseline_check_short_or_placeholder_secret_key_fails(self):
        # Short key
        with override_settings(SECRET_KEY="short-key"):
            with self.assertRaises(CommandError):
                call_command("baseline_check", stdout=io.StringIO())

        # Placeholder key
        placeholder = "django-insecure-" + "c" * 45
        with override_settings(SECRET_KEY=placeholder):
            with self.assertRaises(CommandError):
                out = io.StringIO()
                try:
                    call_command("baseline_check", stdout=out)
                except CommandError:
                    self.assertNotIn(placeholder, out.getvalue())
                    raise

    def test_baseline_check_database_in_staticfiles_fails(self):
        good_key = "d" * 55
        with tempfile.TemporaryDirectory() as tmp_dir:
            static_dir = Path(tmp_dir) / "static"
            static_dir.mkdir()
            exposed_db = static_dir / "db.sqlite3"
            exposed_db.touch()

            with override_settings(
                SECRET_KEY=good_key,
                DEBUG=False,
                ALLOWED_HOSTS=["example.com"],
                DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": str(exposed_db)}},
                STATICFILES_DIRS=[str(static_dir)],
            ):
                with self.assertRaises(CommandError):
                    call_command("baseline_check", stdout=io.StringIO())

    def test_baseline_check_never_prints_secret_key(self):
        secret_value = "super-secret-canary-token-9876543210-unique-string-12345"
        with override_settings(SECRET_KEY=secret_value, DEBUG=False, ALLOWED_HOSTS=["example.com"]):
            out = io.StringIO()
            call_command("baseline_check", stdout=out)
            output = out.getvalue()
            self.assertNotIn(secret_value, output)
            self.assertIn("SECRET_KEY", output)


class DeploymentConfigTests(SimpleTestCase):
    def test_static_root_configured(self):
        self.assertIsNotNone(settings.STATIC_ROOT)
        self.assertTrue(bool(settings.STATIC_ROOT))

    def test_whitenoise_middleware_configured(self):
        self.assertIn("whitenoise.middleware.WhiteNoiseMiddleware", settings.MIDDLEWARE)

    def test_collectstatic_runs_in_temp_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with override_settings(STATIC_ROOT=Path(tmp_dir) / "collected"):
                out = io.StringIO()
                call_command("collectstatic", interactive=False, verbosity=1, stdout=out)
                output = out.getvalue()
                self.assertIn("static files", output.lower())
                collected_files = list((Path(tmp_dir) / "collected").rglob("*"))
                self.assertTrue(len(collected_files) > 0)





