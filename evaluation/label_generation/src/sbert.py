import os
import warnings

from sentence_transformers import SentenceTransformer
from vector_cache import VectorCache

PRETRAINED_MODELS = [
    "all-mpnet-base-v2",  # best performance
    "multi-qa-mpnet-base-dot-v1",
    "all-distilroberta-v1",
    "all-MiniLM-L12-v2",
    "multi-qa-distilbert-cos-v1",
    "all-MiniLM-L6-v2",  # best performance-speed tradeoff
    "multi-qa-MiniLM-L6-cos-v1",
    "paraphrase-multilingual-mpnet-base-v2",
    "paraphrase-albert-small-v2",
    "paraphrase-multilingual-MiniLM-L12-v2",
    "paraphrase-MiniLM-L3-v2",
    "distiluse-base-multilingual-cased-v1",
    "distiluse-base-multilingual-cased-v2",
]


alias_map = {
    "speed": "all-MiniLM-L6-v2",
    "performance": "all-mpnet-base-v2",
    "paraphrase": "paraphrase-MiniLM-L3-v2",
}


class SBERT(VectorCache):
    def __init__(self, model="performance", *, batch_size=16, cache_only=False):
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        model = alias_map.get(model, model)
        if model not in PRETRAINED_MODELS:
            warnings.warn(f"{model} is not one of the recommended models")
        super().__init__(model, batch_size=batch_size)
        self.model_name = model
        if not cache_only:
            self.model = SentenceTransformer(model)
            self.max_sequence_length = self.model.get_max_seq_length()
            self.special_tokens = list(self.model.tokenizer.special_tokens_map.values())

    def embed(self, texts):
        return self.model.encode(texts, batch_size=len(texts))
