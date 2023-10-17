import asyncio
import inspect
from functools import wraps

from fastapi.exceptions import HTTPException
from util.aio import wait_first
from util.thread import CancableThread


async def _check_disconnected(request):
    while not await request.is_disconnected():
        await asyncio.sleep(1)


def cancel_on_disconnect(func):
    @wraps(func)
    async def wrapper(**kwargs):
        request = kwargs["request"]
        if inspect.iscoroutinefunction(func):
            called = func(**kwargs)
        else:
            called = CancableThread(target=lambda: func(**kwargs)).execute()
        called = asyncio.ensure_future(called)
        checker = _check_disconnected(request)
        result, done_coro = await wait_first([checker, called])
        if done_coro is checker:
            called.cancel()
            raise HTTPException(503)
        return result

    return wrapper
