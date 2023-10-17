from ._transformers import build_transformers_model

Model = build_transformers_model(
    "OpenAssistant/pythia-12b-sft-v8-7k-steps",
    set_pad_token=True,
    tokenizer_kwargs={"model_max_length": 2048},
)
