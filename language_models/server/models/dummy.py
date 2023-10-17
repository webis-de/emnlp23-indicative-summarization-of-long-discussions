import random
import time

from pydantic import Field


class Model:
    TYPE = "generation"

    def __call__(self, batch, top_p: int = Field(0.1, ge=0.0, le=1.0)):
        results = []
        for prompt in batch:
            results.append(f"processed: {top_p} {prompt}")
        time.sleep(random.expovariate(10))
        return results
