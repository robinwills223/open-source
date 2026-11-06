"""Fixture tests verifying all profiles in examples/profiles/valid and invalid.
"""
from pathlib import Path
import pytest
from tools.validate_profile import validate_file

REPO_ROOT = Path(__file__).resolve().parent.parent
VALID_DIR = REPO_ROOT / "examples" / "profiles" / "valid"
INVALID_DIR = REPO_ROOT / "examples" / "profiles" / "invalid"

valid_files = list(VALID_DIR.glob("*.yaml"))
invalid_files = list(INVALID_DIR.glob("*.yaml"))


@pytest.mark.parametrize("file_path", valid_files, ids=lambda p: p.name)
def test_valid_profile_fixtures(file_path):
    code, findings, data = validate_file(file_path)
    assert code == 0, f"Expected 0 for {file_path.name}, got {code}. Findings: {[f.message for f in findings]}"
    assert len(findings) == 0


@pytest.mark.parametrize("file_path", invalid_files, ids=lambda p: p.name)
def test_invalid_profile_fixtures(file_path):
    # Extract expected failure substring from header comment
    with open(file_path, "r", encoding="utf-8") as f:
        first_line = f.readline()
    assert "EXPECTED_FAILURE:" in first_line, f"{file_path.name} missing # EXPECTED_FAILURE: header"
    expected_reason = first_line.split("EXPECTED_FAILURE:")[1].strip()

    code, findings, data = validate_file(file_path)
    assert code in (1, 2), f"Expected failure exit code (1 or 2) for {file_path.name}, got {code}"
    
    all_messages = " ".join(f.message for f in findings)
    assert expected_reason.lower() in all_messages.lower(), (
        f"{file_path.name} expected '{expected_reason}', but findings were: {[f.message for f in findings]}"
    )

