from collections.abc import Callable

from nomia.config import load_config
from nomia.discovery import discover_untracked_functions


def audit_untracked(
    config_path: str | None = None,
    verbose: bool = False,
) -> list[str]:
    config = load_config(config_path)

    functions = discover_untracked_functions(config=config, verbose=verbose)

    qualified_names: list[str] = []

    for func in functions:
        qualified_names.append(f"{func.__module__}.{func.__qualname__}")

    return sorted(set(qualified_names))