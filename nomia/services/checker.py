from pathlib import Path

from nomia.config import load_config
from nomia.discovery import discover_functions
from nomia.fingerprint import fingerprint_function
from nomia.state import load_state

from nomia.models import (
    code_changed_issue,
    missing_implementation_issue,
    not_validated_issue,
)


def check(config_path: str | None = None, verbose: bool = False) -> list[dict]:
    config = load_config(config_path)
    project_root: Path = config["_project_root"]

    discovered = discover_functions(config=config, verbose=verbose)
    saved_state = load_state(project_root)

    issues: list[dict] = []

    declared_rule_ids = {rule["id"] for rule in config.get("rules", [])}
    discovered_rule_ids = {rule_id for rule_id, _func in discovered}

    missing_rule_ids = sorted(declared_rule_ids - discovered_rule_ids)

    for rule_id in missing_rule_ids:
        issues.append(missing_implementation_issue(rule_id))

    for rule_id, func in discovered:
        qualified_name = f"{func.__module__}.{func.__qualname__}"
        current_hash = fingerprint_function(func)

        saved = (
            saved_state.get("rules", {})
            .get(rule_id, {})
            .get("functions", {})
            .get(qualified_name)
        )

        if saved is None:
            issues.append(not_validated_issue(rule_id, qualified_name))
            continue

        if saved["code_hash"] != current_hash:
            issues.append(code_changed_issue(rule_id, qualified_name))

    return issues