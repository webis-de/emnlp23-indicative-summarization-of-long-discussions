from collections import OrderedDict


class CacheDict(OrderedDict):
    def __init__(self, *args, cache_len: int = 100000, **kwargs):
        assert cache_len > 0
        self.cache_len = cache_len
        super().__init__(*args, **kwargs)

    def _clean(self):
        iterator = iter(self)
        while len(self) > self.cache_len:
            super().__delitem__(next(iterator))

    def _add(self, key, value):
        super().__setitem__(key, value)
        super().move_to_end(key)

    def __setitem__(self, key, value):
        self._add(key, value)
        self._clean()

    def batch_add(self, mapping):
        for key, value in mapping.items():
            self._add(key, value)
        self._clean()

    def __getitem__(self, key):
        val = super().__getitem__(key)
        super().move_to_end(key)
        return val

    def batch_get(self, keys):
        return [self.get(key) for key in keys]
