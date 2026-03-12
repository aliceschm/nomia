from nomia.discovery import discover_functions
from nomia.fingerprint import fingerprint_function
from nomia.state import load_state


def check(project_root: str = "example_app") -> list[dict]:
    discovered = discover_functions(project_root)
    saved_state = load_state()

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