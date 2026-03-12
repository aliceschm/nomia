from nomia.discovery import discover_functions
from nomia.fingerprint import fingerprint_function
from nomia.state import save_state


def validate(project_root: str = "example_app") -> dict:
    discovered = discover_functions(project_root)

    state = {"rules": {}}

    for rule_id, func in discovered:
        qualified_name = f"{func.__module__}.{func.__qualname__}"
        code_hash = fingerprint_function(func)

        state["rules"].setdefault(rule_id, {"functions": {}})
        state["rules"][rule_id]["functions"][qualified_name] = {
            "code_hash": code_hash
        }

    save_state(state)
    return state