import torch

from ._transformers import build_transformers_model

Model = build_transformers_model(
    "tiiuae/falcon-40b",
    inclusive_stopping_strings={'["': ["]"]},
    dtype=torch.bfloat16,
    set_pad_token=True,
    trust_remote_code=True,
)
