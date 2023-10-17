import asyncio

import kthread

from .aio import to_thread


class CancableThread(kthread.KThread):
    def run(self):
        self.result = None
        self.exc = None
        try:
            self.result = self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.exc = e

    async def execute(self):
        self.start()
        try:
            await to_thread(self.join)
            if self.exc:
                raise self.exc
            return self.result
        except asyncio.CancelledError:
            if self.is_alive():
                self.terminate()
            raise
