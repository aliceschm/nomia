import hashlib
import inspect
from collections.abc import Callable


def fingerprint_function(func: Callable) -> str:
    try:
        source = inspect.getsource(func)
    except (OSError, TypeError):
        # fallback: use module + qualname
        fallback = f"{func.__module__}.{func.__qualname__}"
        return hashlib.sha256(fallback.encode("utf-8")).hexdigest()

    normalized = source.strip().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()