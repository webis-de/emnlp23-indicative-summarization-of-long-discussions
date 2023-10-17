import string


class MissingKey:
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return MissingKeyStr("".join([self.key, "!s"]))

    def __repr__(self):  # Supports {key!r}
        return MissingKeyStr("".join([self.key, "!r"]))

    def __format__(self, spec):
        if spec:
            return "".join(["{", self.key, ":", spec, "}"])
        return "".join(["{", self.key, "}"])

    def __getitem__(self, i):
        return MissingKey("".join([self.key, "[", str(i), "]"]))

    def __getattr__(self, name):
        return MissingKey("".join([self.key, ".", name]))


class MissingKeyStr(MissingKey, str):
    def __init__(self, key):
        self.key = "".join([key.key, "!s"]) if isinstance(key, MissingKey) else key


class SafeFormatter(string.Formatter):
    def __init__(self, raise_unused=False):
        self.raise_unused = raise_unused

    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            return kwargs.get(key, MissingKey(key))
        return super().get_value(key, args, kwargs)

    def check_unused_args(self, used_args, _, kwargs):
        if self.raise_unused:
            unused_args = set(kwargs) - used_args
            if unused_args:
                raise KeyError(", ".join(unused_args))
