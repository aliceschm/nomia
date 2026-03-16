from pathlib import Path

from nomia.config import load_config
from nomia.discovery import discover_functions
from nomia.fingerprint import fingerprint_function
from nomia.state import save_state


def validate(config_path: str | None = None) -> dict:
    config = load_config(config_path)
    project_root: Path = config["_project_root"]

    discovered = discover_functions(config_path)

    state = {"rules": {}}

    for rule_id, func in discovered:
        qualified_name = f"{func.__module__}.{func.__qualname__}"
        code_hash = fingerprint_function(func)

        state["rules"].setdefault(rule_id, {"functions": {}})
        state["rules"][rule_id]["functions"][qualified_name] = {
            "code_hash": code_hash
        }

    save_state(project_root, state)
    return state