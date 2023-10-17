import asyncio


async def wait_first(coros, ensure_finished=False):
    futures = [asyncio.ensure_future(c) for c in coros]
    try:
        done, _ = await asyncio.wait(futures, return_when=asyncio.FIRST_COMPLETED)
        done_future = done.pop()
        done_coro = coros[futures.index(done_future)]
        return done_future.result(), done_coro
    finally:
        for future in futures:
            future.cancel()
        if ensure_finished:
            for future in futures:
                try:
                    await future
                except:
                    pass


async def to_thread(func, *args, **kwargs):
    return await asyncio.get_running_loop().run_in_executor(None, func, *args, **kwargs)
