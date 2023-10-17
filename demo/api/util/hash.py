from hashlib import sha1

from util.iterator import chain_interleave


def _bytes(data):
    yield data


def _str_bytes(data):
    yield str(data).encode()


def _list_bytes(data):
    yield b"["
    data = map(to_bytes, data)
    yield from chain_interleave(data, b",")
    yield b"]"


TYPES = [
    (str, b"str", _str_bytes),
    (list, b"list", _list_bytes),
    (tuple, b"list", _list_bytes),
    (int, b"int", _str_bytes),
    (float, b"float", _str_bytes),
    (bytes, b"bytes", _bytes),
]


def to_bytes(data):
    for type_, prefix, serializer in TYPES:
        if isinstance(data, type_):
            yield prefix
            yield from serializer(data)
            return
    raise ValueError(f"unsupported type {type(data)}")


def to_hash(data):
    hasher = sha1()
    for b in to_bytes(data):
        hasher.update(b)
    return hasher.digest()
