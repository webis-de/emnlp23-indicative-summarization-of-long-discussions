import asyncio

from utils.aio import parallel
from utils.event import EventBox


class RequestManager:
    def __init__(self, request, response_handler, check_timeout=1):
        self.request = request
        self.check_timeout = check_timeout
        self.disconnect_event = asyncio.Event()
        self.response_handler = response_handler

    async def check_disconnected(self):
        while not await self.request.is_disconnected():
            await asyncio.sleep(self.check_timeout)
        self.disconnect_event.set()

    async def send_to_workers(self, data, workers):
        async with parallel(self.check_disconnected()):
            event_box = EventBox(self.disconnect_event, self.response_handler)
            workers.submit(event_box, data)
            await event_box.wait()
            return event_box.make_response(to_response=True)
