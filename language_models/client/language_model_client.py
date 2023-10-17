from .client_base import ClientBase


class LLMClient(ClientBase):
    def __call__(
        self,
        batch,
        max_new_tokens=None,
        stopping_strings=None,
        raise_overflow=True,
        with_meta=False,
    ):
        is_single = not isinstance(batch, list)
        if is_single:
            batch = [batch]
        args = {"batch": batch}
        if max_new_tokens is not None:
            args["max_new_tokens"] = max_new_tokens
        if stopping_strings is not None:
            args["stopping_strings"] = stopping_strings
        result = self._post("/", json=args, data_only=False)
        generated = []
        for element in result["data"]:
            if raise_overflow:
                overflow = element["size"]["overflow"]
                if overflow != 0:
                    raise ValueError(f"overflow occurred: {overflow}")
            generated.append(element)
        if is_single:
            (generated,) = generated
        if with_meta:
            return generated, result["meta"]
        return generated
