import asyncio

import motor.motor_asyncio
from bson.objectid import ObjectId
from config import MONGODB_URL

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)


class PostInterface:
    def __init__(self):
        self.collection = client.reddit.posts
        self._cache_lock = asyncio.Lock()
        self._previous_count = None

    async def _was_changed(self):
        current_count = await self.collection.count_documents({})
        was_changed = (
            self._previous_count is None or current_count != self._previous_count
        )
        self._previous_count = current_count
        return was_changed

    async def list(self):
        async with self._cache_lock:
            if await self._was_changed():
                result = await self.collection.aggregate(
                    [
                        {
                            "$set": {
                                "labelsOTA": {"$objectToArray": "$labels"},
                            },
                        },
                        {
                            "$project": {
                                "id": "$_id",
                                "title": 1,
                                "url": 1,
                                "num_comments": 1,
                                "labels": "$labelsOTA.k",
                            },
                        },
                        {"$sort": {"_id": -1}},
                    ],
                ).to_list(None)
                self._cached_post_list = result
            return self._cached_post_list

    async def insert(self, post):
        return await self.collection.insert_one(post)

    async def get(self, id):
        if isinstance(id, str):
            id = ObjectId(id)
        result = await self.collection.find_one({"_id": id})
        if result:
            result["id"] = result["_id"]
        return result

    async def labels(self, id):
        if isinstance(id, str):
            id = ObjectId(id)
        result = await self.collection.find_one(
            {"_id": id}, {"labels": 1, "meta": 1, "result": 1, "root": 1, "frames": 1}
        )
        return result


P = PostInterface()
