from ._transformers import build_transformers_model

Model = build_transformers_model(
    "huggyllama/llama-65b", inclusive_stopping_strings={'["': ["]"]}
)
