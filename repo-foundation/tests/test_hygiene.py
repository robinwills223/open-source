"""Tests for tools/check_repo_hygiene.py using temporary test files.
"""
from tools.check_repo_hygiene import check_file


def test_clean_file_passes(tmp_path):
    f = tmp_path / "clean.txt"
    f.write_text("This is a clean document with no secrets or personal paths.\n", encoding="utf-8")
    findings = check_file(f)
    assert len(findings) == 0


def test_allowed_placeholders_pass(tmp_path):
    f = tmp_path / "license.txt"
    f.write_text("Copyright (c) [YEAR] [YOUR NAME]\nContact [SECURITY CONTACT] for advisories.\n", encoding="utf-8")
    findings = check_file(f)
    assert len(findings) == 0


def test_private_key_detected(tmp_path):
    f = tmp_path / "key.txt"
    # Construct test string dynamically to avoid false-positive detection in test file itself
    dummy_key = "-----BEGIN RSA " + "PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n"
    f.write_text(dummy_key, encoding="utf-8")
    findings = check_file(f)
    assert any(ftype == "SECRET" for _, ftype, _ in findings)


def test_github_token_detected(tmp_path):
    f = tmp_path / "token.txt"
    dummy_token = "GITHUB_TOKEN = '" + "ghp_" + ("a" * 36) + "'\n"
    f.write_text(dummy_token, encoding="utf-8")
    findings = check_file(f)
    assert any(ftype == "SECRET" for _, ftype, _ in findings)


def test_aws_access_key_detected(tmp_path):
    f = tmp_path / "aws.txt"
    dummy_aws = "AWS_KEY = '" + "AKIA" + "IOSFODNN7EXAMPLE'\n"
    f.write_text(dummy_aws, encoding="utf-8")
    findings = check_file(f)
    assert any(ftype == "SECRET" for _, ftype, _ in findings)


def test_personal_path_detected_windows(tmp_path):
    f = tmp_path / "path_win.txt"
    dummy_win = "Location: C:" + "\\Users\\" + "johndoe\\file.py\n"
    f.write_text(dummy_win, encoding="utf-8")
    findings = check_file(f)
    assert any(ftype == "PERSONAL_PATH" for _, ftype, _ in findings)


def test_personal_path_detected_unix(tmp_path):
    f = tmp_path / "path_unix.txt"
    dummy_unix = "Location: /" + "Users/" + "johndoe/file.py\n"
    f.write_text(dummy_unix, encoding="utf-8")
    findings = check_file(f)
    assert any(ftype == "PERSONAL_PATH" for _, ftype, _ in findings)


def test_unreplaced_placeholder_detected(tmp_path):
    f = tmp_path / "bad_placeholder.txt"
    dummy_ph = "Contact [" + "INSERT " + "EMAIL HERE] or [" + "TODO" + ": fix this].\n"
    f.write_text(dummy_ph, encoding="utf-8")
    findings = check_file(f)
    assert any(ftype == "UNREPLACED_PLACEHOLDER" for _, ftype, _ in findings)
