#!/usr/bin/env python

import argparse
import json
import sys
from collections import OrderedDict, defaultdict
from itertools import islice
from os import environ
from pathlib import Path

import dotenv
import numpy as np
import pandas as pd

from clean import ERROR_INDICATORS, clean, count_words
from render import STYLES

language_models_path = str(
    Path(__file__).resolve().parent.parent.parent / "language_models"
)
sys.path.insert(0, language_models_path)

from experiment_definitions import RENAME_MAP as READABLE_RENAME_MAP

parser = argparse.ArgumentParser()
parser.add_argument("--style", default="markdown", choices=list(STYLES.keys()))
args = parser.parse_args()

style = args.style

PROJECT_PATH = Path(__file__).parent.parent.parent
DATA_PATH = Path(__file__).parent / "data"
GENERATED_PATH = DATA_PATH / "generated"
CLUSTERS_PATH = DATA_PATH / "clusters.json"
BERTSCORE_PATH = DATA_PATH / "BERTScore.json"
ROUGE_PATH = DATA_PATH / "ROUGE.json"
DATASET_PATH = PROJECT_PATH / "dataset" / f"default.json"
OLD_HYPOTHESES = DATA_PATH / "old_hypotheses.json"


def cluster_is_valid(key):
    return int(key) >= 0


def read_discussions():
    return json.loads(DATASET_PATH.read_text())


def get_labeled_clusters(discussions, ignore_none=False):
    labeled_clusters = []
    for discussion_id, discussion in discussions.items():
        for cluster_id, cluster in discussion["clusters"].items():
            if "label" in cluster and cluster_is_valid(cluster_id):
                if not ignore_none or cluster["label"] is not None:
                    labeled_clusters.append((discussion_id, cluster_id))
    return labeled_clusters


RENAME_DICT = {
    "gptneox": "gpt_neox",
    "t0": "t0pp",
    "opt66": "opt_66b",
    "gpt3": "text_davinci_003",
}

BEST_PROMPTS = {
    "t0_output_type": "title",
    "bloom": "dialog title",
    "gptneox": "qa discussion topic",
    "opt66": "qa topic",
    "gpt3": "instruct gpt phrase",
}


clusters = json.loads(CLUSTERS_PATH.read_text())


class Hypotheses(list):
    def __init__(self):
        super().__init__()
        old_hypotheses = self.load_old_hypotheses()

        for file in GENERATED_PATH.glob("*.json"):
            generated = json.loads(file.read_text())["generated"]
            for id, hypothesis in generated.items():
                model = file.stem
                key = {"model": model, "id": id}
                self.append((key, hypothesis))

        for model, values in old_hypotheses.items():
            for id, hypothesis in values.items():
                key = {"model": model, "id": id}
                self.append((key, hypothesis))

    @staticmethod
    def load_old_hypotheses():
        try:
            old_hypotheses = json.loads(OLD_HYPOTHESES.read_text())
        except OSError:
            old_hypotheses = {}
            discussions = read_discussions()
            keys = get_labeled_clusters(discussions, ignore_none=True)
            old_hypotheses = defaultdict(dict)
            for discussion_key, cluster_key in keys:
                id = f"{discussion_key}-{cluster_key}"
                cluster = discussions[discussion_key]["clusters"][cluster_key]
                for model_name, sub_key in BEST_PROMPTS.items():
                    generated = cluster[model_name][sub_key]
                    if "t0" in model_name:
                        model_name = "t0"
                    model_name = RENAME_DICT.get(model_name, model_name)
                    old_model = f"{model_name} (old)"
                    old_hypotheses[old_model][id] = generated
            OLD_HYPOTHESES.write_text(json.dumps(old_hypotheses))
        return old_hypotheses


def get_bertscorer():
    from client import MetricClient
    dotenv.load_dotenv()
    MODEL_HOSTS = environ["MODEL_HOSTS"].split()
    return MetricClient("bertscore", host=MODEL_HOSTS)


from rouge import Rouge as _Rouge


class Rouge:
    def __init__(self):
        self.rouge = _Rouge()

    def __call__(self, batch):
        hypotheses, references = zip(*batch)
        result = self.rouge.get_scores(hypotheses, references)
        return [
            {metric: e[metric]["f"] for metric in ["rouge-1", "rouge-2", "rouge-l"]}
            for e in result
        ]


def get_rouge():
    return Rouge()


def ibatch(*args, batch_size):
    args = [iter(e) for e in args]
    if len(args) > 1:
        it = zip(*args)
        while e := list(islice(it, batch_size)):
            yield tuple(zip(*e))
    else:
        (it,) = args
        while e := list(islice(it, batch_size)):
            yield tuple(e)


REFERENCE_RENAME = OrderedDict([("human", "Reference"), ("text_davinci_003", "GPT3.5")])

RENAME_MAP = {
    **READABLE_RENAME_MAP,
    **REFERENCE_RENAME,
    "gpt_4": "GPT4",
    "t0pp": "T0",
    "opt_66b": "OPT",
    "gpt_35_turbo": "ChatGPT",
    "llama_30b_supercot": "LLaMA-CoT",
}


def rename(model_name, ttfamily=(style == "latex"), split_char=" "):
    model_first, *rest = model_name.split(split_char)
    if model_first in RENAME_MAP:
        model_first = RENAME_MAP[model_first]
        if ttfamily:
            model_first = rf"\ttfamily{{{model_first}}}"
    return split_char.join([model_first, *rest])


class Scores:
    def __init__(self, get_metric, path, hypotheses, clusters, metric_map):
        self.path = Path(path)
        self.metric_map = OrderedDict(metric_map)
        self.load()
        pairs = []
        for key, hypothesis in hypotheses:
            hypothesis = clean(hypothesis)
            id = key["id"]
            references = clusters[id]["references"]
            id_dict = self.scores.get(key["model"], {}).get(id, {})
            for type_key, reference in references.items():
                if type_key not in id_dict:
                    reference = clean(reference)
                    pairs.append(
                        (
                            {**key, "type": type_key},
                            (hypothesis, reference),
                        )
                    )
        if pairs:
            metric = get_metric()
            for batch in ibatch(pairs, batch_size=128):
                keys, pairs = map(list, zip(*batch))
                example_scores = metric(pairs)
                for key, score in zip(keys, example_scores):
                    id_dict = self.scores.setdefault(key["model"], {})
                    reference_dict = id_dict.setdefault(key["id"], {})
                    reference_dict[key["type"]] = score
            self.write()

    def load(self):
        try:
            self.scores = json.loads(self.path.read_text())
        except OSError:
            self.scores = {}

    def write(self):
        self.path.write_text(json.dumps(self.scores))

    def aggregate(self):
        series = []
        for model, value in self.scores.items():
            aggregated = defaultdict(list)
            for score_dict in value.values():
                for reference_name, metrics in score_dict.items():
                    for metric_name, score in metrics.items():
                        metric_name = self.metric_map.get(metric_name, metric_name)
                        aggregated[f"{reference_name}:{metric_name}"].append(score)
            aggregated = pd.DataFrame(aggregated).mean(axis=0)
            aggregated.name = model
            series.append(aggregated)
        all_columns = [
            f"{reference_name}:{metric_name}"
            for reference_name in REFERENCE_RENAME.keys()
            for metric_name in self.metric_map.values()
        ]
        df = pd.concat(series, axis=1).T
        df = df[all_columns]
        df.columns = [rename(e, split_char=":") for e in df.columns]
        return df


def transpose_dict(data):
    all_keys = None
    transposed = defaultdict(dict)
    for key, value in data.items():
        this_keys = set(value.keys())
        if all_keys is None:
            all_keys = this_keys
        if this_keys != all_keys:
            raise ValueError("key missmatch")
        for sub_key, sub_value in value.items():
            transposed[sub_key][key] = sub_value
    return dict(transposed)


def render(df, precision=2):
    sub_columns = [e.replace(" - ", ":") for e in df.columns]
    if all(":" in e for e in sub_columns):
        df.columns = pd.MultiIndex.from_tuples(
            [column.split(":") for column in sub_columns]
        )
    df = df.sort_index()
    df = df.reset_index(names=["Model"])
    df["Model"] = df["Model"].map(rename)
    print()
    print(STYLES[style](df, precision))
    print()


hyps = Hypotheses()


hypo_length = defaultdict(list)
for key, hypothesis in hyps:
    hypo_length[key["model"]].append(count_words(clean(hypothesis)))
hypo_length = {
    key: {
        "Length:Min": np.min(value),
        "Length:Max": np.max(value),
        "Length:Mean": np.mean(value),
    }
    for key, value in hypo_length.items()
}
hypo_length = pd.DataFrame(transpose_dict(hypo_length))
# render(hypo_length, precision=1)


all_errors = defaultdict(int)
for key, hypothesis in hyps:
    if any(e in hypothesis.lower() for e in ERROR_INDICATORS):
        all_errors[key["model"]] += 1
error_df = pd.Series(all_errors)
error_df.name = "Errors"
error_df = error_df.to_frame()
print("# Errors")
render(error_df, precision=0)

BERTSCORE_METRIC_MAP = OrderedDict(
    [
        ("precision", "P"),
        ("recall", "R"),
        ("f-measure", "F1"),
    ]
)

bertscore_scores = Scores(
    get_bertscorer, BERTSCORE_PATH, hyps, clusters, BERTSCORE_METRIC_MAP
)
print("# Mean BERTScore and length statistics for label generation")
aggregated = bertscore_scores.aggregate()
aggregated = pd.concat([aggregated, hypo_length], axis=1)
render(aggregated, precision=2)

ROUGE_METRIC_MAP = OrderedDict(
    [
        ("rouge-1", "R-1"),
        ("rouge-2", "R-2"),
        ("rouge-l", "R-LCS"),
    ]
)

rouge_scores = Scores(get_rouge, ROUGE_PATH, hyps, clusters, ROUGE_METRIC_MAP)
print("# Mean ROUGE for label generation")
aggregated = rouge_scores.aggregate() * 100
render(aggregated, precision=2)
