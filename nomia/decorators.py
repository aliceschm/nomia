from collections.abc import Callable
from functools import wraps
from typing import Any


def rule(rule_id: str):
    if not isinstance(rule_id, str) or not rule_id.strip():
        raise ValueError("Rule id must be a non-empty string.")

    normalized_rule_id = rule_id.strip()

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        setattr(wrapper, "__nomia_rule__", normalized_rule_id)
        return wrapper

    return decorator