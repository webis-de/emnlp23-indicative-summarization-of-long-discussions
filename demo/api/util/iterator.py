from itertools import chain


def interleave(l, value):
    l = iter(l)
    try:
        e = next(l)
        yield e
        while e := next(l):
            yield value
            yield e
    except StopIteration:
        pass


def chain_interleave(l, value):
    yield from chain.from_iterable(interleave(l, (value,)))
