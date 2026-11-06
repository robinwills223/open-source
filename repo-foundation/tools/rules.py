"""Authoritative reference implementation of repo-foundation rules.
Sole authority: docs/05-rules-single-source.md.
"""
from dataclasses import dataclass
from typing import Literal

FindingType = Literal["ERROR", "BLOCK", "HALT"]
ORDER_TO_SCOPE = {1: "small", 2: "medium", 3: "enterprise"}


@dataclass(frozen=True)
class Finding:
    type: FindingType
    message: str
    code: str = ""


def derive_scope(profile: dict) -> str:
    """Derive scope_level deterministically via highest-signal-wins rule.
    Cites: docs/05 Section 1.1 & Section 1.2. (team_size is decoupled per Section 1).
    """
    users = profile.get("expected_users", 0)
    u = 1 if users < 500 else (2 if users < 10000 else 3)
    s = 3 if profile.get("data_sensitivity") == "health" else (2 if profile.get("data_sensitivity") == "payments_direct" else 1)
    v = 2 if profile.get("validation_stage") == "scaling" else 1
    return ORDER_TO_SCOPE[max(u, s, v)]


def expected_capabilities(profile: dict) -> dict[str, bool]:
    """Compute expected capability switch states from profile signals.
    Cites: docs/05 Section 6 (Authoritative Capability Trigger Matrix).
    """
    scope = derive_scope(profile)
    users = profile.get("expected_users", 0)
    team = profile.get("team_size", 1)
    sens = profile.get("data_sensitivity", "none")
    stage = profile.get("validation_stage", "idea")
    shape = profile.get("product_shape", "small_tool")
    sig = set(profile.get("escalation_signals") or [])

    bg_jobs = "slow_sync_calls" in sig
    return {
        "docker": team >= 2,
        "postgres": scope in ("medium", "enterprise") or "sqlite_lock_contention" in sig,
        "redis": bg_jobs or "high_traffic_bursts" in sig,
        "background_jobs": bg_jobs,
        "ci": team >= 2,
        "error_monitoring": scope in ("medium", "enterprise"),
        "compliance_checklist": sens in ("payments_direct", "health") or scope == "enterprise",
        "rate_limiting": users >= 500 or scope in ("medium", "enterprise") or shape == "multi_user_saas" or "high_traffic_bursts" in sig,
        "minimum_viable_backup": stage in ("validated_pre_revenue", "paying_customers", "scaling"),
        "backups": scope in ("medium", "enterprise"),
    }


def check_overrides(profile: dict) -> list[Finding]:
    """Validate developer overrides and capability alignment.
    Cites: docs/05 Section 10 (Developer Overrides Protocol).
    """
    findings: list[Finding] = []
    overrides = profile.get("overrides") or []
    stage = profile.get("validation_stage", "idea")
    sens = profile.get("data_sensitivity", "none")

    # docs/05 Section 10.1 #1: non_technical_founder cannot override
    if profile.get("audience") == "non_technical_founder" and overrides:
        findings.append(Finding("ERROR", "Non-technical founders cannot specify overrides. Overrides are restricted to developer profiles.", "OVERRIDE_FOUNDER_FORBIDDEN"))

    override_map: dict[str, dict] = {}
    for ov in overrides:
        cap, val, reason = ov.get("capability"), ov.get("value"), ov.get("reason", "")
        if not cap:
            continue
        override_map[cap] = ov
        # docs/05 Section 10.1 #2: technical reason >= 10 characters
        if len(reason.strip()) < 10:
            findings.append(Finding("ERROR", f"Override for '{cap}' must have a technical justification of at least 10 characters.", "OVERRIDE_REASON_TOO_SHORT"))
        # docs/05 Section 10.1 #3: Inviolable Safety Floors
        if cap == "minimum_viable_backup" and val is False and stage in ("validated_pre_revenue", "paying_customers", "scaling"):
            findings.append(Finding("ERROR", "Safety floor violation: minimum_viable_backup cannot be disabled when validation_stage is validated_pre_revenue, paying_customers, or scaling.", "SAFETY_FLOOR_MVB"))
        if cap == "compliance_checklist" and val is False and sens in ("payments_direct", "health"):
            findings.append(Finding("ERROR", "Safety floor violation: compliance_checklist cannot be disabled when data_sensitivity is payments_direct or health.", "SAFETY_FLOOR_COMPLIANCE"))
        if cap == "postgres" and val is False and profile.get("hosting_target") == "paas_ephemeral":
            findings.append(Finding("ERROR", "Safety floor violation: postgres cannot be disabled when hosting_target is paas_ephemeral (causes SQLite data loss).", "SAFETY_FLOOR_PAAS_EPHEMERAL"))

    # docs/05 Section 10.1 #2: capability may differ only if matching override exists
    expected = expected_capabilities(profile)
    actual = profile.get("capabilities") or {}
    for cap, exp_val in expected.items():
        act_val = actual.get(cap)
        if act_val is None:
            continue
        if act_val != exp_val:
            if cap not in override_map or override_map[cap].get("value") != act_val:
                findings.append(Finding("ERROR", f"Capability '{cap}' is set to {act_val}, but expected {exp_val} based on triggers, with no matching override.", "CAPABILITY_MISMATCH"))
        elif cap in override_map and override_map[cap].get("value") != act_val:
            findings.append(Finding("ERROR", f"Override specifies '{cap}: {override_map[cap].get('value')}', but capabilities has '{act_val}'.", "OVERRIDE_VALUE_MISMATCH"))

    return findings


def check_safeguards(profile: dict) -> list[Finding]:
    """Evaluate architectural safeguards, deployment blockers, and budget conflicts.
    Cites: docs/05 Section 1.3, Section 7.2, Section 12.
    """
    findings: list[Finding] = []
    scope = derive_scope(profile)
    caps = profile.get("capabilities") or {}
    budget = profile.get("budget_range")

    # docs/05 Section 1.3: Enterprise halt
    if scope == "enterprise":
        findings.append(Finding("HALT", "Enterprise scope is formally specified but automated scaffolding is not yet implemented. Scaffolding must halt; please consider a scoped-down prototype.", "ENTERPRISE_HALT"))

    # docs/05 Section 7.2: Ephemeral PaaS + SQLite block
    if profile.get("hosting_target") == "paas_ephemeral" and not caps.get("postgres", False):
        findings.append(Finding("BLOCK", "Deployment blocked: Running SQLite on ephemeral PaaS will erase data on redeploy. Attach a persistent volume (paas_persistent) or enable postgres: true before proceeding.", "EPHEMERAL_SQLITE_BLOCKED"))

    # docs/05 Section 12: Budget conflicts
    if scope == "medium" and budget == "zero":
        findings.append(Finding("BLOCK", "Budget conflict: Derived scope is Medium, but budget is $0. Confirm provider free tiers or remain on SQLite.", "BUDGET_CONFLICT_MEDIUM_ZERO"))
    elif scope == "enterprise" and budget in ("zero", "bootstrap"):
        findings.append(Finding("BLOCK", "Budget conflict: Enterprise requirements cannot be hosted under a $0 or bootstrap budget.", "BUDGET_CONFLICT_ENTERPRISE_LOW"))

    return findings
