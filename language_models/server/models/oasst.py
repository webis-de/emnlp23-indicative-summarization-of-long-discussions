from ._transformers import build_transformers_model

Model = build_transformers_model(
    "Yhyu13/oasst-rlhf-2-llama-30b-7k-steps-hf",
    tokenizer_kwargs={"model_max_length": 2048},
)
