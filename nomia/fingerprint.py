import hashlib
import inspect
import json
from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any


def _normalize_rule_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()

    if isinstance(value, Mapping):
        return {
            str(key): _normalize_rule_value(value[key])
            for key in sorted(value, key=lambda item: str(item))
        }

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_normalize_rule_value(item) for item in value]

    return value


def fingerprint_rule(rule: Mapping[str, Any]) -> str:
    normalized = _normalize_rule_value(rule)
    serialized = json.dumps(
        normalized,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )

    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def fingerprint_function(func: Callable) -> str:
    try:
        source = inspect.getsource(
            func.__wrapped__ if hasattr(func, "__wrapped__") else func
        )
    except (OSError, TypeError):
        code = getattr(func, "__code__", None)

        if code is not None:
            fallback = "|".join(
                [
                    str(func.__module__),
                    str(func.__qualname__),
                    str(code.co_argcount),
                    str(code.co_kwonlyargcount),
                    str(code.co_posonlyargcount),
                    str(code.co_nlocals),
                    str(code.co_consts),
                    str(code.co_names),
                ]
            )
        else:
            fallback = f"{func.__module__}.{func.__qualname__}"

        return hashlib.sha256(fallback.encode("utf-8")).hexdigest()

    normalized = source.strip().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()
