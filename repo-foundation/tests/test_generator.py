"""Tests for project generator tool (tools/generate_project.py).
"""

import subprocess
import sys
from pathlib import Path
import pytest
from tools.generate_project import generate_project

REPO_ROOT = Path(__file__).resolve().parent.parent
VALID_DIR = REPO_ROOT / "examples" / "profiles" / "valid"
INVALID_DIR = REPO_ROOT / "examples" / "profiles" / "invalid"


@pytest.mark.parametrize(
    "profile_name",
    [
        "tiny-internal-tool.yaml",
        "small-paid-tool.yaml",
        "beta-tool-paas-resolved.yaml",
    ],
)
def test_generator_supported_profiles(tmp_path, profile_name):
    profile_path = VALID_DIR / profile_name
    out_dir = tmp_path / f"out_{profile_path.stem}"

    code = generate_project(profile_path, out_dir)
    assert code == 0, f"Expected 0 for {profile_name}, got {code}"

    # Verify expected files exist
    assert (out_dir / "manage.py").is_file()
    assert (out_dir / "requirements.txt").is_file()
    assert (out_dir / "project.profile.yaml").is_file()
    assert (out_dir / "DECISIONS-FOR-FOUNDER.md").is_file()
    assert (out_dir / "config" / "settings.py").is_file()
    assert (out_dir / "records" / "models.py").is_file()

    # Verify NO Docker, CI, or optional packages exist
    assert not (out_dir / "Dockerfile").exists()
    assert not (out_dir / "docker-compose.yml").exists()
    assert not (out_dir / ".github").exists()

    reqs = (out_dir / "requirements.txt").read_text(encoding="utf-8")
    for blocked_pkg in ("redis", "celery", "psycopg", "sentry-sdk", "django-ratelimit"):
        assert blocked_pkg not in reqs.lower()


@pytest.mark.parametrize(
    "profile_name",
    [
        "small-duo-team.yaml",      # team_size: 2, docker: true, ci: true
        "demand-test.yaml",         # product_shape: demand_test
        "multi-user-saas.yaml",     # multi_user_saas, medium scope
        "saas-hosted-checkout.yaml",# multi_user_saas, medium scope
        "saas-solo-bootstrap.yaml", # multi_user_saas, rate_limiting: true
    ],
)
def test_generator_unsupported_profiles_exit_2(tmp_path, profile_name, capsys):
    profile_path = VALID_DIR / profile_name
    out_dir = tmp_path / f"out_{profile_path.stem}"

    code = generate_project(profile_path, out_dir)
    assert code == 2, f"Expected exit code 2 for unsupported {profile_name}, got {code}"
    assert not out_dir.exists(), "Output directory should not be created for unsupported profile"

    captured = capsys.readouterr()
    assert "outside v0.1 alpha support scope" in captured.out


@pytest.mark.parametrize(
    "profile_name",
    [
        "beta-tool-paas.yaml",
        "health-halt.yaml",
        "founder-override.yaml",
        "safety-floor-mvb.yaml",
        "scope-mismatch.yaml",
    ],
)
def test_generator_invalid_and_blocked_profiles(tmp_path, profile_name):
    profile_path = INVALID_DIR / profile_name
    out_dir = tmp_path / f"out_{profile_path.stem}"

    code = generate_project(profile_path, out_dir)
    assert code in (1, 2), f"Expected exit code 1 or 2 for {profile_name}, got {code}"
    assert not out_dir.exists(), "Output directory should not be created for invalid profile"


def test_generator_refuses_non_empty_dir(tmp_path):
    out_dir = tmp_path / "non_empty"
    out_dir.mkdir()
    (out_dir / "existing.txt").write_text("already here", encoding="utf-8")

    profile_path = VALID_DIR / "tiny-internal-tool.yaml"
    code = generate_project(profile_path, out_dir)
    assert code == 1


def test_generated_project_own_test_suite_passes(tmp_path):
    """Run the generated project's own Django test suite."""
    profile_path = VALID_DIR / "tiny-internal-tool.yaml"
    out_dir = tmp_path / "tiny_tool_app"

    code = generate_project(profile_path, out_dir)
    assert code == 0

    res = subprocess.run(
        [sys.executable, "manage.py", "test"],
        cwd=str(out_dir),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Generated project tests failed:\n{res.stdout}\n{res.stderr}"
    assert "OK" in res.stderr or "OK" in res.stdout


def test_generator_validation_links_for_idea_stage(tmp_path):
    profile_path = VALID_DIR / "tiny-internal-tool.yaml"
    out_dir = tmp_path / "idea_app"
    assert generate_project(profile_path, out_dir) == 0

    founder_doc = (out_dir / "DECISIONS-FOR-FOUNDER.md").read_text(encoding="utf-8")
    assert "01-before-you-build.md" in founder_doc
    assert "02-interview-script.md" in founder_doc
    assert "03-demand-test.md" in founder_doc
    assert "04-running-a-pilot.md" not in founder_doc


def test_generator_validation_links_for_validated_stage(tmp_path):
    profile_path = VALID_DIR / "small-paid-tool.yaml"
    out_dir = tmp_path / "paid_app"
    assert generate_project(profile_path, out_dir) == 0

    founder_doc = (out_dir / "DECISIONS-FOR-FOUNDER.md").read_text(encoding="utf-8")
    assert "04-running-a-pilot.md" in founder_doc
    assert "pilot-tracker.csv" in founder_doc


