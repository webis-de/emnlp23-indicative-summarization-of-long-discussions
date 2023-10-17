import random
from threading import Thread

import requests


class ThreadWithReturnValue(Thread):
    def run(self):
        self.result = None
        self.exc = None
        try:
            self.result = self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.exc = e

    def finish(self):
        if self.exc:
            raise self.exc
        return self.result


def check_host(host):
    try:
        response = requests.get(f"{host}/health")
    except requests.exceptions.ConnectionError:
        return None
    result = response.json()
    if not result["success"]:
        return None
    try:
        return host, result["meta"]["model"]
    except KeyError:
        pass
    return None


def find_host(model, hosts, select_random=True):
    threads = [
        ThreadWithReturnValue(target=check_host, args=(host,))
        for host in hosts
        if host.startswith("http")
    ]
    for thread in threads:
        thread.start()
    found = []
    for thread in threads:
        thread.join()
        result = thread.finish()
        if result:
            found.append(result)
    valid = [host for host, server_model in found if model == server_model]
    if not select_random:
        return valid
    if not valid:
        raise ValueError(
            f"none of the configured hosts is running '{model}', found: {found}"
        )
    if len(valid) > 1:
        host = random.choice(valid)
    else:
        (host,) = valid
    return host
