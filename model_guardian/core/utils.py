from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, TypeVar

from types import MappingProxyType
from collections.abc import Mapping

T = TypeVar("T")

_DEFAULT_EXECUTOR: ThreadPoolExecutor | None = None


def get_default_executor() -> ThreadPoolExecutor:
    global _DEFAULT_EXECUTOR
    if _DEFAULT_EXECUTOR is None:
        _DEFAULT_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="mg-exec")
    return _DEFAULT_EXECUTOR


async def run_sync(fn: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Run a sync function without blocking the event loop."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(get_default_executor(), lambda: fn(*args, **kwargs))


def deep_freeze(obj: Any) -> Any:
    """Recursively freeze common mutable containers.

    This is used to enforce a stricter "no mutable raw artifacts" policy for
    Prediction.raw. We do *not* attempt to freeze arbitrary user classes.
    """
    # dict -> mapping proxy (immutable)
    if isinstance(obj, dict):
        return MappingProxyType({k: deep_freeze(v) for k, v in obj.items()})

    # mapping types (e.g. MappingProxyType already) -> copy to proxy
    if isinstance(obj, Mapping) and not isinstance(obj, (str, bytes)):
        return MappingProxyType({k: deep_freeze(v) for k, v in obj.items()})

    # list/tuple -> tuple
    if isinstance(obj, (list, tuple)):
        return tuple(deep_freeze(v) for v in obj)

    # set -> frozenset
    if isinstance(obj, set):
        return frozenset(deep_freeze(v) for v in obj)

    # numpy arrays: copy & make read-only if available
    try:  # pragma: no cover
        import numpy as np

        if isinstance(obj, np.ndarray):
            arr = obj.copy()
            try:
                arr.setflags(write=False)
            except Exception:
                pass
            return arr
    except Exception:
        pass

    return obj
