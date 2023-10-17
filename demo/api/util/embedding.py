from itertools import islice


def ibatch(*args, batch_size):
    args = [iter(e) for e in args]
    if len(args) > 1:
        it = zip(*args)
        while e := list(islice(it, batch_size)):
            yield tuple(zip(*e))
    else:
        (it,) = args
        while e := list(islice(it, batch_size)):
            yield tuple(e)


def batch_embed(values, embedder, *, extras=None, batch_size=16, with_batch=False):
    if extras is not None:
        if len(values) != len(extras):
            raise ValueError("length of values and extras needs to be same")
        values = list(zip(values, extras))
    batches = ibatch(values, batch_size=batch_size)
    for batch in batches:
        if extras is not None:
            batch, extra = zip(*batch)
        result = (embedder(batch),)
        if extras is not None:
            result = result + (extra,)
        if with_batch:
            result = (batch,) + result
        if len(result) == 1:
            (result,) = result
        yield result


def batch_embed(values, embedder, *, extras=None, batch_size=16, with_batch=False):
    if extras is not None:
        if len(values) != len(extras):
            raise ValueError("length of values and extras needs to be same")
        values = list(zip(values, extras))
    batches = ibatch(values, batch_size=batch_size)
    for batch in batches:
        if extras is not None:
            batch, extra = zip(*batch)
        result = (embedder(batch),)
        if extras is not None:
            result = result + (extra,)
        if with_batch:
            result = (batch,) + result
        if len(result) == 1:
            (result,) = result
        yield result
