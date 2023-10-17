from ._transformers import ModelTypes, build_transformers_model

Model = build_transformers_model(
    "bigscience/T0pp",
    model_type=ModelTypes.ENCODER_DECODER,
    tokenizer_kwargs={"model_max_length": 1024},
)
