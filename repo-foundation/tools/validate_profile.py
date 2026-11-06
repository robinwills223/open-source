"""Command-line profile validator with schema and rule validation.
Cites: docs/05-rules-single-source.md
Usage: python tools/validate_profile.py <path/to/profile.yaml>
Exit codes: 0 = valid, 1 = invalid, 2 = blocked or halted.
"""
import sys, json
from pathlib import Path
import yaml, jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.rules import Finding, derive_scope, check_overrides, check_safeguards

DEFAULT_SCHEMA = Path(__file__).resolve().parent.parent / "schemas" / "project.profile.schema.json"


def validate_profile_dict(profile: dict, schema_path: Path = DEFAULT_SCHEMA) -> tuple[int, list[Finding]]:
    findings: list[Finding] = []
    # 1. Schema Validation
    try:
        with open(schema_path, "r", encoding="utf-8") as sf:
            schema = json.load(sf)
        validator = jsonschema.Draft7Validator(schema)
        for err in sorted(validator.iter_errors(profile), key=lambda e: list(e.path)):
            field = ".".join(str(p) for p in err.path) or "root"
            findings.append(Finding("ERROR", f"Schema error at '{field}': {err.message}", "SCHEMA_ERROR"))
    except Exception as exc:
        return 1, [Finding("ERROR", f"Failed schema validation: {exc}", "SCHEMA_LOAD_ERROR")]

    # 2. Scope Derivation Check (docs/05 Section 1)
    derived = derive_scope(profile)
    declared = profile.get("scope_level")
    if declared and declared != derived:
        findings.append(Finding("ERROR", f"Scope mismatch: declared '{declared}', but profile inputs derive '{derived}'.", "SCOPE_MISMATCH"))

    # 3. Overrides & Capability Alignment (docs/05 Section 10)
    findings.extend(check_overrides(profile))

    # 4. Safeguards (docs/05 Section 1.3, 7.2, 12)
    findings.extend(check_safeguards(profile))

    if any(f.type == "ERROR" for f in findings):
        return 1, findings
    if any(f.type in ("BLOCK", "HALT") for f in findings):
        return 2, findings
    return 0, findings


def validate_file(file_path: Path | str, schema_path: Path = DEFAULT_SCHEMA) -> tuple[int, list[Finding], dict | None]:
    p = Path(file_path)
    if not p.is_file():
        return 1, [Finding("ERROR", f"File not found: {p}", "FILE_NOT_FOUND")], None
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as exc:
        return 1, [Finding("ERROR", f"Invalid YAML in {p}: {exc}", "YAML_SYNTAX_ERROR")], None
    if not isinstance(data, dict):
        return 1, [Finding("ERROR", f"Profile must be a YAML mapping: {p}", "INVALID_ROOT")], None
    code, findings = validate_profile_dict(data, schema_path)
    return code, findings, data


def format_report(file_path: str, code: int, findings: list[Finding], data: dict | None) -> str:
    name = data.get("name", "unknown") if data else "unknown"
    status_str = "VALID (Pass)" if code == 0 else ("INVALID (Failed)" if code == 1 else "HALTED / BLOCKED")
    lines = [
        f"=== Profile Validation Report ===",
        f"File:    {file_path} (Project: {name})",
        f"Result:  Exit {code} -> {status_str}",
    ]
    if findings:
        lines.append("Findings:")
        for f in findings:
            lines.append(f"  [{f.type}] {f.message}")
    else:
        lines.append("All schema invariants, capability triggers, and safeguards passed.")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/validate_profile.py <path/to/profile.yaml>")
        sys.exit(1)
    ret, findings, data = validate_file(sys.argv[1])
    print(format_report(sys.argv[1], ret, findings, data))
    sys.exit(ret)
