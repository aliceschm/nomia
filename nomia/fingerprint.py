import hashlib
import inspect
from collections.abc import Callable


def fingerprint_function(func: Callable) -> str:
    try:
        source = inspect.getsource(func)
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