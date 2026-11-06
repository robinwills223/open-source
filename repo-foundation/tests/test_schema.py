"""Tests for JSON Schema validation and conditional allOf if/then invariants.

Cites: schemas/project.profile.schema.json
"""
import json
from pathlib import Path
import pytest
import jsonschema

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "project.profile.schema.json"


@pytest.fixture(scope="module")
def schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def base_valid_profile():
    return {
        "profile_version": 1,
        "name": "test-project",
        "description": "Baseline valid profile for schema testing.",
        "audience": "junior_developer",
        "product_shape": "small_tool",
        "scope_level": "small",
        "stack": "django",
        "expected_users": 10,
        "team_size": 1,
        "data_sensitivity": "none",
        "budget_range": "zero",
        "validation_stage": "idea",
        "hosting_target": "local",
        "capabilities": {
            "docker": False,
            "postgres": False,
            "redis": False,
            "background_jobs": False,
            "ci": False,
            "error_monitoring": False,
            "compliance_checklist": False,
            "rate_limiting": False,
            "minimum_viable_backup": False,
            "backups": False,
        },
    }


def is_valid(profile, schema):
    validator = jsonschema.Draft7Validator(schema)
    return validator.is_valid(profile)


# Rule 1: Non-technical founder overrides prohibition
def test_schema_rule_founder_overrides(schema):
    p_ok = base_valid_profile()
    p_ok["audience"] = "non_technical_founder"
    assert is_valid(p_ok, schema)

    p_bad = base_valid_profile()
    p_bad["audience"] = "non_technical_founder"
    p_bad["overrides"] = [{"capability": "docker", "value": True, "reason": "Founder containers"}]
    assert not is_valid(p_bad, schema)


# Rule 2: Validation stage >= validated_pre_revenue requires MVB
def test_schema_rule_stage_requires_mvb(schema):
    p_ok = base_valid_profile()
    p_ok["validation_stage"] = "validated_pre_revenue"
    p_ok["capabilities"]["minimum_viable_backup"] = True
    assert is_valid(p_ok, schema)

    p_bad = base_valid_profile()
    p_bad["validation_stage"] = "validated_pre_revenue"
    p_bad["capabilities"]["minimum_viable_backup"] = False
    assert not is_valid(p_bad, schema)


# Rule 3: Direct payments or health requires compliance_checklist
def test_schema_rule_sensitivity_requires_compliance(schema):
    p_ok = base_valid_profile()
    p_ok["data_sensitivity"] = "payments_direct"
    p_ok["capabilities"]["compliance_checklist"] = True
    assert is_valid(p_ok, schema)

    p_bad = base_valid_profile()
    p_bad["data_sensitivity"] = "payments_direct"
    p_bad["capabilities"]["compliance_checklist"] = False
    assert not is_valid(p_bad, schema)


# Rule 4: Ephemeral PaaS requires postgres
def test_schema_rule_ephemeral_paas_requires_postgres(schema):
    p_ok = base_valid_profile()
    p_ok["hosting_target"] = "paas_ephemeral"
    p_ok["capabilities"]["postgres"] = True
    assert is_valid(p_ok, schema)

    p_bad = base_valid_profile()
    p_bad["hosting_target"] = "paas_ephemeral"
    p_bad["capabilities"]["postgres"] = False
    assert not is_valid(p_bad, schema)


# Rule 5: slow_sync_calls requires background_jobs and redis
def test_schema_rule_slow_sync_calls(schema):
    p_ok = base_valid_profile()
    p_ok["escalation_signals"] = ["slow_sync_calls"]
    p_ok["capabilities"]["background_jobs"] = True
    p_ok["capabilities"]["redis"] = True
    assert is_valid(p_ok, schema)

    p_bad = base_valid_profile()
    p_bad["escalation_signals"] = ["slow_sync_calls"]
    p_bad["capabilities"]["background_jobs"] = False
    p_bad["capabilities"]["redis"] = True
    assert not is_valid(p_bad, schema)


# Rule 6: sqlite_lock_contention requires postgres
def test_schema_rule_sqlite_lock_contention(schema):
    p_ok = base_valid_profile()
    p_ok["escalation_signals"] = ["sqlite_lock_contention"]
    p_ok["capabilities"]["postgres"] = True
    assert is_valid(p_ok, schema)

    p_bad = base_valid_profile()
    p_bad["escalation_signals"] = ["sqlite_lock_contention"]
    p_bad["capabilities"]["postgres"] = False
    assert not is_valid(p_bad, schema)


# Rule 7: high_traffic_bursts requires redis
def test_schema_rule_high_traffic_bursts(schema):
    p_ok = base_valid_profile()
    p_ok["escalation_signals"] = ["high_traffic_bursts"]
    p_ok["capabilities"]["redis"] = True
    assert is_valid(p_ok, schema)

    p_bad = base_valid_profile()
    p_bad["escalation_signals"] = ["high_traffic_bursts"]
    p_bad["capabilities"]["redis"] = False
    assert not is_valid(p_bad, schema)

