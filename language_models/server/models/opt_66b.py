from ._transformers import build_transformers_model

Model = build_transformers_model(
    "facebook/opt-66b",
    set_pad_token=True,
    inclusive_stopping_strings={'"': ['"'], '["': ["]"]},
    tokenizer_kwargs={"use_fast": False, "model_max_length": 2048},
)
