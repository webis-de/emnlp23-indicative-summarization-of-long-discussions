import re

import numpy as np

SPACE_RE = re.compile(r"\s+")


def get_diff_indexes(arr):
    if len(arr) == 0:
        return []
    diff_arr = np.diff(arr)
    (indices,) = np.where(diff_arr != 0)
    indices += 1
    indices = [0, *(int(e) for e in indices)]
    return indices


def normalize(text):
    return SPACE_RE.sub(" ", text).strip()


def pseudo_join(texts, join_string=" "):
    if not texts:
        return []
    first, *rest = texts
    rest = [f"{join_string}{e}" for e in rest]
    return [first, *rest]


def trim_text(
    client,
    template,
    text,
    max_new_tokens,
    max_length=None,
    model_max_length=None,
    backoff=0,
):
    text = pseudo_join([normalize(e) for e in text])
    if "{input}" in template:
        *template_prefix, template_suffix = template.split("{input}")
        template_prefix = "{input}".join(template_prefix)
    else:
        template_prefix, template_suffix = template, ""
    if max_length is not None and max_length > 1:
        model_max_length = max_length
    else:
        model_max_length = model_max_length or client.meta()["model_max_length"]
        if max_length is not None:
            model_max_length *= max_length
    model_max_length = int(model_max_length)
    size_info = client.count_tokens([template_prefix, *text, template_suffix])
    template_start, *counts, template_end = size_info["counts"]
    max_tokens = (
        model_max_length
        - max_new_tokens
        - template_start
        - template_end
        - size_info["num"]["special"]
        - backoff
    )
    cum_tokens = np.cumsum(counts)
    is_less = cum_tokens < max_tokens
    diff_indexes = get_diff_indexes(is_less)[1:]
    if diff_indexes:
        (upper,) = diff_indexes
        selected_text = text[:upper]
    else:
        selected_text = text
    return "".join(selected_text)
