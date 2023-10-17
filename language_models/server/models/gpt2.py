import torch

from ._transformers import build_transformers_model

Model = build_transformers_model(
    "gpt2",
    inclusive_stopping_strings={'"': ['"'], '["': ["]"]},
    dtype=torch.float32,
    set_pad_token=True,
)
