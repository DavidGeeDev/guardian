from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, TypeVar

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
