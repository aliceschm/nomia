from collections.abc import Callable

_REGISTRY: list[tuple[str, Callable]] = []


def register(rule_id: str, func: Callable) -> None:
    _REGISTRY.append((rule_id, func))


def get_registry() -> list[tuple[str, Callable]]:
    return list(_REGISTRY)


def clear_registry() -> None:
    _REGISTRY.clear()