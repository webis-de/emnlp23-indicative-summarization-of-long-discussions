from .client_base import ClientBase


class MetricClient(ClientBase):
    def __call__(
        self,
        batch,
        select=None,
        with_meta=False,
    ):
        is_single = not isinstance(batch, list)
        if is_single:
            batch = [batch]
        args = {"batch": batch}
        if select is not None:
            args["select"] = select
        result = self._post("/", json=args, data_only=False)
        scores = result["data"]
        if is_single:
            (scores,) = scores
        if with_meta:
            return scores, result["meta"]
        return scores
