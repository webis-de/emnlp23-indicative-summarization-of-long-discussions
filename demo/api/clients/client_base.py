import requests

from .hosts import find_host


class LLMError(Exception):
    def __init__(self, meta, *args, **kwargs):
        self.meta = meta
        super().__init__(*args, **kwargs)


class ServerError(LLMError):
    def __init__(self, errors, *args, **kwargs):
        self.errors = errors
        super().__init__(*args, **kwargs)


class UserError(LLMError):
    pass


class ClientBase:
    def __init__(self, model, host):
        self.model = model
        if isinstance(host, str):
            self.host = host
        elif isinstance(host, (list, tuple)):
            self.host = find_host(model, host)
        else:
            raise ValueError("host has to be string or list")

    def _verify(self, response):
        result = response.json()
        if not result["success"]:
            if result["error"] == "USER":
                raise UserError(result["meta"], result["message"])
            elif "errors" in result:
                raise ServerError(
                    result["errors"],
                    result["meta"],
                    "server answered with error",
                )
            else:
                raise LLMError(result["meta"], "unknown error")
        server_model = result["meta"]["model"]
        if server_model != self.model:
            raise ValueError(
                f"The client is build for '{self.model}', but the server is running '{server_model}'"
            )
        return result

    def _get(self, url, *args, data_only=True, **kwargs):
        result = self._verify(requests.get(f"{self.host}{url}", *args, **kwargs))
        if data_only:
            return result["data"]
        return result

    def _post(self, url, *args, data_only=True, **kwargs):
        result = self._verify(requests.post(f"{self.host}{url}", *args, **kwargs))
        if data_only:
            return result["data"]
        return result

    def meta(self):
        return self._get("/health", data_only=False)["meta"]

    def count_tokens(self, text, indicate_shared=False, data_only=True):
        return self._post(
            "/tokenizer/count",
            json={"text": text, "indicate_shared": indicate_shared},
            data_only=data_only,
        )

    def __call__(self, *args, **kwargs):
        raise NotImplementedError
