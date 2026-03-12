from collections.abc import Callable
from functools import wraps
from typing import Any

from nomia.registry import register


def rule(rule_id: str):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        setattr(wrapper, "__nomia_rule__", rule_id)
        register(rule_id, wrapper)
        return wrapper

    return decorator