"""Automated tests for records tracker starter app.

Covers:
- Model behavior and timestamps
- Strict login enforcement on all views
- Cross-user ownership isolation (returns 404 on unowned records)
- Spreadsheet formula injection protection in CSV exports
- Status filtering
- Production settings behavior and manage.py check --deploy
"""

import io
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings
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

