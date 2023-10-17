import re

from .gpt_client import OpenAIClient
from .language_model_client import LLMClient

NON_ALPHANUM_RE = re.compile(r"[^a-z0-9_]")


def get_llm_client(model, host=None, api_key=None):
    if model in OpenAIClient.MODELS:
        return OpenAIClient(model=model, api_key=api_key)
    model = NON_ALPHANUM_RE.sub("", model.lower().replace("-", "_").replace("+", "p"))
    return LLMClient(model=model, host=host)
