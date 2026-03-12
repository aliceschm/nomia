import hashlib
import inspect
from collections.abc import Callable


def fingerprint_function(func: Callable) -> str:
    source = inspect.getsource(func)
    normalized = source.strip().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()