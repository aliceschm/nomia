from pathlib import Path

from nomia.config import load_config
from nomia.discovery import discover_functions
from nomia.fingerprint import fingerprint_function, fingerprint_rule
from nomia.state import load_state

from nomia.models import (
    code_changed_issue,
    missing_implementation_issue,
    not_validated_issue,
    implementation_removed_issue,
    rule_removed_issue,
    rule_content_changed_issue,
    STATE_CODE_HASH_KEY,
    STATE_FUNCTIONS_KEY,
    STATE_RULE_HASH_KEY,
    STATE_RULES_KEY,
)


def check(config_path: str | None = None, verbose: bool = False) -> list[dict]:
    config = load_config(config_path)
    project_root: Path = config["_project_root"]

    raw_discovered = discover_functions(config=config, verbose=verbose)
    seen: set[tuple[str, str]] = set()
    discovered: list[tuple[str, object]] = []

    for rule_id, func in raw_discovered:
        qualified_name = f"{func.__module__}.{func.__qualname__}"
        key = (rule_id, qualified_name)

        if key in seen:
            continue

        seen.add(key)
        discovered.append((rule_id, func))
    
    saved_state = load_state(project_root)

    issues: list[dict] = []

    rules_by_id = {rule["id"]: rule for rule in config.get("rules", [])}
    declared_rule_ids = set(rules_by_id)
    discovered_rule_ids = {rule_id for rule_id, _func in discovered}

    missing_rule_ids = sorted(declared_rule_ids - discovered_rule_ids)

    for rule_id in missing_rule_ids:
        issues.append(missing_implementation_issue(rule_id))

    saved_rule_ids = set(saved_state.get(STATE_RULES_KEY, {}).keys())
    
    removed_rule_ids = sorted(saved_rule_ids - declared_rule_ids)

    for rule_id in removed_rule_ids:
        issues.append(rule_removed_issue(rule_id))

    saved_rules = saved_state.get(STATE_RULES_KEY, {})

    for rule_id, rule in sorted(rules_by_id.items()):
        saved_rule = saved_rules.get(rule_id)

        if saved_rule is None:
            continue

        if saved_rule.get(STATE_RULE_HASH_KEY) != fingerprint_rule(rule):
            issues.append(rule_content_changed_issue(rule_id))

    discovered_functions_by_rule: dict[str, set[str]] = {}

    for rule_id, func in discovered:
        qualified_name = f"{func.__module__}.{func.__qualname__}"
        discovered_functions_by_rule.setdefault(rule_id, set()).add(qualified_name)

    for rule_id, rule_data in saved_rules.items():
        saved_functions = rule_data.get(STATE_FUNCTIONS_KEY, {})
        discovered_functions = discovered_functions_by_rule.get(rule_id, set())

        removed_functions = sorted(set(saved_functions.keys()) - discovered_functions)

        for function_name in removed_functions:
            issues.append(implementation_removed_issue(rule_id, function_name))

    for rule_id, func in discovered:
        qualified_name = f"{func.__module__}.{func.__qualname__}"
        current_hash = fingerprint_function(func)

        saved = (
            saved_state.get(STATE_RULES_KEY, {})
            .get(rule_id, {})
            .get(STATE_FUNCTIONS_KEY, {})
            .get(qualified_name)
        )

        if saved is None:
            issues.append(not_validated_issue(rule_id, qualified_name))
            continue

        if saved[STATE_CODE_HASH_KEY] != current_hash:
            issues.append(code_changed_issue(rule_id, qualified_name))

    return issues
