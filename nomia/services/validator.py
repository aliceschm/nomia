from pathlib import Path

from nomia.config import load_config
from nomia.discovery import discover_functions
from nomia.fingerprint import fingerprint_function
from nomia.state import save_state

from nomia.models import (
    STATE_CODE_HASH_KEY,
    STATE_FUNCTIONS_KEY,
    STATE_RULES_KEY,
    add_function_to_state,
    create_empty_state,
)


def validate(config_path: str | None = None, verbose: bool = False) -> dict:
    config = load_config(config_path)
    project_root: Path = config["_project_root"]

    discovered = discover_functions(config=config, verbose=verbose)

    state = create_empty_state()

    seen: set[tuple[str, str]] = set()

    for rule_id, func in sorted(
        discovered,
        key=lambda item: (item[0], f"{item[1].__module__}.{item[1].__qualname__}")
    ):
        qualified_name = f"{func.__module__}.{func.__qualname__}"

        key = (rule_id, qualified_name)
        if key in seen:
            continue

        seen.add(key)

        code_hash = fingerprint_function(func)

        add_function_to_state(
            state,
            rule_id,
            qualified_name,
            code_hash,
        )

    save_state(project_root, state)
    return state
