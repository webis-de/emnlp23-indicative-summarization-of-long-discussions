from abc import ABC, abstractmethod

import numpy as np
from util.cache import CacheDict
from util.embedding import batch_embed
from util.hash import to_hash


class VectorCache(ABC):
    def __init__(self, model, batch_size, prefix=True):
        if not isinstance(prefix, str) and prefix:
            prefix = self.__class__.__name__
        self.MODEL_KEY = f"{prefix} {model}".encode()
        self.batch_size = batch_size
        self.cache = CacheDict()

    @abstractmethod
    def embed(self, multiple):
        raise NotImplemented()

    def post_process(self, embeddings, **_):
        return np.array(embeddings)

    def _embed(self, multiple):
        return list(self.embed(list(multiple)))

    def _key(self, single):
        return self.MODEL_KEY + to_hash(single)

    def _from_cache(self, keys):
        keys = list(set(keys))
        cached = self.cache.batch_get(keys)
        return {key: e for key, e in zip(keys, cached) if e is not None}

    def _add_to_cache(self, embed_dict):
        self.cache.batch_add(embed_dict)

    def _batch_embed(self, multiple_dict, batch_size, add_to_cache=True):
        multiple_keys, multiple = zip(*multiple_dict.items())
        embedded = {}
        for batch_embedded, batch_keys in batch_embed(
            multiple, self._embed, extras=multiple_keys, batch_size=batch_size
        ):
            embed_dict = dict(zip(batch_keys, batch_embedded))
            if add_to_cache:
                self._add_to_cache(embed_dict)
            embedded.update(embed_dict)
        return embedded

    def _embed_multiple(self, multiple, batch_size, from_cache):
        if batch_size < 1:
            raise ValueError(f"invalid batchsize: {batch_size}")
        keys = [self._key(single) for single in multiple]

        if from_cache:
            input_dict = dict(zip(keys, multiple))
            unique_keys = set(input_dict.keys())
            cached = self._from_cache(unique_keys)
            uncached_keys = unique_keys - set(cached.keys())
            uncached = {key: input_dict[key] for key in uncached_keys}
        else:
            cached, uncached = {}, dict(zip(keys, multiple))

        if uncached:
            embedded = self._batch_embed(uncached, batch_size, add_to_cache=from_cache)
            cached.update(embedded)
        return [cached[key] for key in keys]

    def __call__(self, multiple, batch_size=None, from_cache=True):
        if hasattr(multiple, "tolist"):
            multiple = multiple.tolist()
        elif hasattr(multiple, "to_list"):
            multiple = multiple.to_list()
        if not isinstance(multiple, (list, tuple)):
            raise ValueError("multiple has to be list or tuple")
        if batch_size is None:
            batch_size = self.batch_size
        embeddings = self._embed_multiple(multiple, batch_size, from_cache=from_cache)
        return self.post_process(embeddings=embeddings, inputs=multiple)
