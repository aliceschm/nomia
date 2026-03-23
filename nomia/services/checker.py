from pathlib import Path

from nomia.config import load_config
from nomia.discovery import discover_functions
from nomia.fingerprint import fingerprint_function
from nomia.state import load_state


def check(config_path: str | None = None, verbose: bool = False) -> list[dict]:
    config = load_config(config_path)
    project_root: Path = config["_project_root"]

    discovered = discover_functions(config_path=config_path, verbose=verbose)
    saved_state = load_state(project_root)

    issues: list[dict] = []

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
            issues.append(
                {
                    "type": "not_validated",
                    "rule_id": rule_id,
                    "function": qualified_name,
                }
            )
            continue

        if saved["code_hash"] != current_hash:
            issues.append(
                {
                    "type": "code_changed",
                    "rule_id": rule_id,
                    "function": qualified_name,
                }
            )

    return issues