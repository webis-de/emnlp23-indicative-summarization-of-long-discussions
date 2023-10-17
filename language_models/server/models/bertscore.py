from typing import Literal, Set, Union

from bert_score import BERTScorer as _BERTScorer
from pydantic import Field

ALL_METRICS = ["precision", "recall", "f-measure"]
METRIC_CHOICES = Literal[tuple(ALL_METRICS)]


class BERTScorer:
    def __init__(self, model="microsoft/deberta-xlarge-mnli", device="cuda:0"):
        self.scorer = _BERTScorer(
            model_type=model, rescale_with_baseline=True, lang="en", device=device
        )

    def __call__(self, batch):
        hypotheses, references = zip(*batch)
        result = self.scorer.score(hypotheses, references, batch_size=len(batch))
        precision, recall, f_measure = result
        return {
            "precision": precision,
            "recall": recall,
            "f-measure": f_measure,
        }


class Model:
    TYPE = "metric"

    PREFERRED_SETTINGS = {
        "num_threads": 1,
        "batch_size": 128,
        "cache_size": 0,
    }

    def __init__(self):
        self.bert_scorer = BERTScorer()

    def __call__(
        self,
        batch,
        select: Union[Set[METRIC_CHOICES], METRIC_CHOICES] = Field(
            set(ALL_METRICS), description="What metric to compute. Can be multiple."
        ),
    ):
        results = self.bert_scorer(batch)
        if isinstance(select, str):
            return results[select].tolist()
        results = {key: results[key].tolist() for key in select}
        keys, scores = zip(*results.items())
        scores = list(zip(*scores))
        results = [dict(zip(keys, score_list)) for score_list in scores]
        return results
