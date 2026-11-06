"""Tests for pure rule functions in tools/rules.py.

Cites: docs/05-rules-single-source.md
"""
import pytest
from tools.rules import (
    derive_scope,
    expected_capabilities,
    check_overrides,
    check_safeguards,
)


# --- Table-Driven Scope Tests at Boundaries (docs/05 Section 1) ---
@pytest.mark.parametrize(
    "users,sensitivity,stage,expected_scope",
    [
        # User boundaries
        (0, "none", "idea", "small"),
        (499, "none", "idea", "small"),
        (500, "none", "idea", "medium"),
        (9999, "none", "idea", "medium"),
        (10000, "none", "idea", "enterprise"),
        # Sensitivity boundaries
        (10, "none", "idea", "small"),
        (10, "personal", "idea", "small"),
        (10, "payments_hosted", "idea", "small"),
        (10, "payments_direct", "idea", "medium"),
        (10, "health", "idea", "enterprise"),
        # Stage boundaries
        (10, "none", "idea", "small"),
        (10, "none", "prototype", "small"),
        (10, "none", "validated_pre_revenue", "small"),
        (10, "none", "paying_customers", "small"),
        (10, "none", "scaling", "medium"),
        # Highest-signal-wins rule
        (10, "payments_direct", "prototype", "medium"),
        (10, "payments_hosted", "scaling", "medium"),
        (10, "health", "scaling", "enterprise"),
        (15000, "none", "prototype", "enterprise"),
        (500, "none", "paying_customers", "medium"),
    ],
)
def test_derive_scope_table(users, sensitivity, stage, expected_scope):
    profile = {
        "expected_users": users,
        "data_sensitivity": sensitivity,
        "validation_stage": stage,
    }
    assert derive_scope(profile) == expected_scope


def test_team_size_decoupled_from_scope():
    """docs/05 Section 1: team_size must never alter derived scope."""
    for team in (1, 2, 5, 20):
        profile = {
            "expected_users": 20,
            "data_sensitivity": "none",
            "validation_stage": "prototype",
            "team_size": team,
        }
        assert derive_scope(profile) == "small"


# --- Table-Driven Capability Trigger Tests (docs/05 Section 6) ---
@pytest.mark.parametrize(
    "team_size,expected_docker_and_ci",
    [
        (1, False),
        (2, True),
        (5, True),
    ],
)
def test_docker_and_ci_triggers(team_size, expected_docker_and_ci):
    profile = {"team_size": team_size}
    caps = expected_capabilities(profile)
    assert caps["docker"] is expected_docker_and_ci
    assert caps["ci"] is expected_docker_and_ci


@pytest.mark.parametrize(
    "scope_users,signals,expected_postgres",
    [
        (50, [], False),  # small without signal
        (500, [], True),  # medium scope
        (50, ["sqlite_lock_contention"], True),  # small with lock contention signal
    ],
)
def test_postgres_triggers(scope_users, signals, expected_postgres):
    profile = {"expected_users": scope_users, "escalation_signals": signals}
    caps = expected_capabilities(profile)
    assert caps["postgres"] is expected_postgres


@pytest.mark.parametrize(
    "signals,expected_bg,expected_redis",
    [
        ([], False, False),
        (["slow_sync_calls"], True, True),  # slow calls triggers bg jobs and redis
        (["high_traffic_bursts"], False, True),  # traffic bursts triggers redis alone
        (["slow_sync_calls", "high_traffic_bursts"], True, True),
    ],
)
def test_background_jobs_and_redis_triggers(signals, expected_bg, expected_redis):
    profile = {"expected_users": 50, "escalation_signals": signals}
    caps = expected_capabilities(profile)
    assert caps["background_jobs"] is expected_bg
    assert caps["redis"] is expected_redis


@pytest.mark.parametrize(
    "users,shape,signals,expected_rate_limiting",
    [
        (10, "small_tool", [], False),
        (500, "small_tool", [], True),  # users >= 500
        (10, "multi_user_saas", [], True),  # saas shape
        (10, "small_tool", ["high_traffic_bursts"], True),  # traffic bursts signal
    ],
)
def test_rate_limiting_triggers(users, shape, signals, expected_rate_limiting):
    profile = {
        "expected_users": users,
        "product_shape": shape,
        "escalation_signals": signals,
    }
    caps = expected_capabilities(profile)
    assert caps["rate_limiting"] is expected_rate_limiting


@pytest.mark.parametrize(
    "stage,expected_mvb",
    [
        ("idea", False),
        ("prototype", False),
        ("validated_pre_revenue", True),
        ("paying_customers", True),
        ("scaling", True),
    ],
)
def test_minimum_viable_backup_triggers(stage, expected_mvb):
    profile = {"validation_stage": stage}
    caps = expected_capabilities(profile)
    assert caps["minimum_viable_backup"] is expected_mvb


@pytest.mark.parametrize(
    "sensitivity,users,expected_compliance",
    [
        ("none", 50, False),
        ("payments_hosted", 50, False),
        ("payments_direct", 50, True),
        ("health", 50, True),
        ("none", 10000, True),  # enterprise scope
    ],
)
def test_compliance_checklist_triggers(sensitivity, users, expected_compliance):
    profile = {"expected_users": users, "data_sensitivity": sensitivity}
    caps = expected_capabilities(profile)
    assert caps["compliance_checklist"] is expected_compliance


# --- Override Tests (docs/05 Section 10) ---
def test_founder_override_rejected():
    profile = {
        "audience": "non_technical_founder",
        "expected_users": 10,
        "capabilities": {"docker": True},
        "overrides": [{"capability": "docker", "value": True, "reason": "Founder wants containers"}],
    }
    findings = check_overrides(profile)
    codes = [f.code for f in findings]
    assert "OVERRIDE_FOUNDER_FORBIDDEN" in codes


def test_senior_override_accepted():
    profile = {
        "audience": "senior_developer",
        "expected_users": 10,
        "team_size": 1,
        "capabilities": {
            "docker": True,  # overridden from False
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
        "overrides": [
            {
                "capability": "docker",
                "value": True,
                "reason": "Developer prefers Docker container for local parity",
            }
        ],
    }
    findings = check_overrides(profile)
    assert len(findings) == 0


def test_short_override_reason_rejected():
    profile = {
        "audience": "senior_developer",
        "expected_users": 10,
        "team_size": 1,
        "capabilities": {"docker": True},
        "overrides": [{"capability": "docker", "value": True, "reason": "too short"}],
    }
    findings = check_overrides(profile)
    assert any(f.code == "OVERRIDE_REASON_TOO_SHORT" for f in findings)


def test_safety_floor_mvb_cannot_be_overridden():
    profile = {
        "audience": "senior_developer",
        "validation_stage": "validated_pre_revenue",
        "capabilities": {"minimum_viable_backup": False},
        "overrides": [
            {
                "capability": "minimum_viable_backup",
                "value": False,
                "reason": "Attempting to skip backup routines during beta test",
            }
        ],
    }
    findings = check_overrides(profile)
    assert any(f.code == "SAFETY_FLOOR_MVB" for f in findings)


def test_safety_floor_compliance_cannot_be_overridden():
    profile = {
        "audience": "senior_developer",
        "data_sensitivity": "payments_direct",
        "capabilities": {"compliance_checklist": False},
        "overrides": [
            {
                "capability": "compliance_checklist",
                "value": False,
                "reason": "Bypassing PCI checklist to accelerate launch date",
            }
        ],
    }
    findings = check_overrides(profile)
    assert any(f.code == "SAFETY_FLOOR_COMPLIANCE" for f in findings)


def test_capability_mismatch_without_override():
    profile = {
        "audience": "senior_developer",
        "team_size": 2,  # triggers docker: True
        "capabilities": {"docker": False},  # set to False without override
    }
    findings = check_overrides(profile)
    assert any(f.code == "CAPABILITY_MISMATCH" for f in findings)


# --- Safeguard Tests (docs/05 Section 1.3, Section 7.2, Section 12) ---
def test_enterprise_halt_safeguard():
    profile = {"expected_users": 15000}
    findings = check_safeguards(profile)
    assert any(f.type == "HALT" and f.code == "ENTERPRISE_HALT" for f in findings)


def test_ephemeral_paas_safeguard_blocks_sqlite():
    profile = {
        "hosting_target": "paas_ephemeral",
        "capabilities": {"postgres": False},
    }
    findings = check_safeguards(profile)
    assert any(f.type == "BLOCK" and f.code == "EPHEMERAL_SQLITE_BLOCKED" for f in findings)


def test_budget_conflict_medium_zero():
    profile = {
        "expected_users": 600,  # derives medium
        "budget_range": "zero",
    }
    findings = check_safeguards(profile)
    assert any(f.type == "BLOCK" and f.code == "BUDGET_CONFLICT_MEDIUM_ZERO" for f in findings)

