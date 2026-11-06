"""Repository hygiene and secret scanner.

Scans tracked text files for:
1. Likely secrets (private keys, credential tokens, secret keys)
2. Personal absolute paths (/Users/..., C:\\Users\\...)
3. Unreplaced placeholders other than allowed [YOUR NAME], [SECURITY CONTACT], [YEAR]

Exit codes: 0 = clean, 1 = hygiene issues found.
"""

import re
import subprocess
import sys
from pathlib import Path

# Allowed placeholders explicitly authorized in repository template files
ALLOWED_PLACEHOLDERS = {
    "[YOUR NAME]",
    "[SECURITY CONTACT]",
    "[YEAR]",
    "[DATE]",
    "[PARTICIPANT-001]",
}

SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"), "Private key detected"),
    (re.compile(r"\b(?:ghp|gho|ghu|ghs)_[A-Za-z0-9_]{36,}\b"), "GitHub token detected"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS Access Key ID detected"),
]

# Personal absolute paths (e.g. C:\Users\<username> or /Users/<username> or /home/<username>)
PERSONAL_PATH_PATTERN = re.compile(
    r"(?:[A-Za-z]:[/\\]Users[/\\](?!(?:Public|Default|\.{3}|<)[/\\])[A-Za-z0-9_.-]{2,}|/(?:Users|home)/(?!(?:runner|circleci|\.{3}|<)[/])[A-Za-z0-9_.-]{2,})",
    re.IGNORECASE,
)

# Unreplaced placeholder patterns: [YOUR ...], [INSERT ...], [TODO...], <YOUR ...>, <INSERT ...>
PLACEHOLDER_PATTERN = re.compile(
    r"(\[(?:YOUR|INSERT|REPLACE|TODO|TBD|PLACEHOLDER)\s+[^\]]+\]|\[(?:TODO|TBD|FIXME)\]|<(?:YOUR|INSERT|REPLACE|TODO)\s+[^>]+>)",
    re.IGNORECASE,
)


def get_target_files(root_dir: Path) -> list[Path]:
    """Get list of files to inspect (tracked by git, or walked if not git)."""
    try:
        res = subprocess.run(
            ["git", "ls-files"],
            cwd=str(root_dir),
            capture_output=True,
            text=True,
            check=True,
        )
        files = [root_dir / line.strip() for line in res.stdout.splitlines() if line.strip()]
        if files:
            return [f for f in files if f.is_file()]
    except Exception:
        pass

    targets: list[Path] = []
    ignored_dirs = {".git", ".pytest_cache", "__pycache__", ".venv", "venv", "node_modules", "dist", "build"}
    for p in root_dir.rglob("*"):
        if p.is_file() and not any(part in ignored_dirs for part in p.parts):
            targets.append(p)
    return targets


def is_binary(file_path: Path) -> bool:
    """Quick check for binary file types."""
    binary_exts = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".sqlite3", ".pyc", ".whl", ".zip", ".tar", ".gz"}
    if file_path.suffix.lower() in binary_exts:
        return True
    try:
        with open(file_path, "tr", encoding="utf-8") as f:
            f.read(1024)
            return False
    except (UnicodeDecodeError, PermissionError):
        return True


def check_file(file_path: Path) -> list[tuple[int, str, str]]:
    """Scan a single file for hygiene issues. Returns list of (line_no, issue_type, message)."""
    findings: list[tuple[int, str, str]] = []
    if is_binary(file_path):
        return findings

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line_no, line in enumerate(f, start=1):
                # 1. Secret patterns
                for pat, desc in SECRET_PATTERNS:
                    if pat.search(line):
                        findings.append((line_no, "SECRET", desc))

                # 2. Personal paths
                if match := PERSONAL_PATH_PATTERN.search(line):
                    findings.append((line_no, "PERSONAL_PATH", f"Absolute personal path detected: '{match.group(0)}'"))

                # 3. Unreplaced placeholders
                for match in PLACEHOLDER_PATTERN.finditer(line):
                    token = match.group(0)
                    if token not in ALLOWED_PLACEHOLDERS:
                        findings.append((line_no, "UNREPLACED_PLACEHOLDER", f"Unreplaced placeholder: '{token}'"))
    except Exception as exc:
        findings.append((0, "READ_ERROR", str(exc)))

    return findings


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1]).resolve()

    files = get_target_files(repo_root)
    self_path = Path(__file__).resolve()
    files = [f for f in files if f.resolve() != self_path]

    total_findings = 0
    for f in files:
        issues = check_file(f)
        if issues:
            rel = f.relative_to(repo_root) if f.is_relative_to(repo_root) else f
            for line_no, issue_type, msg in issues:
                print(f"FAIL: {rel}:{line_no}: [{issue_type}] {msg}")
                total_findings += 1

    if total_findings == 0:
        print(f"PASS: Repo hygiene verified ({len(files)} files checked). No secrets, personal paths, or invalid placeholders found.")
        return 0
    else:
        print(f"Hygiene check failed with {total_findings} finding(s).")
        return 1


if __name__ == "__main__":
    sys.exit(main())
