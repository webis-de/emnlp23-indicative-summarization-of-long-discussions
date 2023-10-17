from pathlib import Path

from ._transformers import build_transformers_model

ROOT_PATH = Path(__file__).parent.parent
SOURCE_PATH = ROOT_PATH / "cache" / "vicuna-7b-delta-v1.1" / "patched"
SETUP_PATH = ROOT_PATH / "setup" / "vicuna_7b.sh"

Model = build_transformers_model(
    SOURCE_PATH,
    setup_path=SETUP_PATH,
    tokenizer_kwargs={"model_max_length": 2048},
)
