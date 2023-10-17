from ._transformers import build_transformers_model

Model = build_transformers_model(
    "EleutherAI/gpt-neox-20b",
    set_pad_token=True,
    inclusive_stopping_strings={'"': ['"'], '["': ["]"]},
    tokenizer_kwargs={"model_max_length": 2048},
)
