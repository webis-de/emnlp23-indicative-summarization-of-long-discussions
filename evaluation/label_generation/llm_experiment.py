#!/usr/bin/env python3

import argparse
import json
import re
import sys
from os import environ
from pathlib import Path

import dotenv
import numpy as np

from experiment_definitions import ALL_EXPERIMENTS, MODEL_LOOKUP

language_models_path = str(
    Path(__file__).resolve().parent.parent.parent / "language_models"
)
sys.path.insert(0, language_models_path)


from experiment_tools import Experiments

dotenv.load_dotenv()

MODEL_HOSTS = environ["MODEL_HOSTS"].split()
OPENAI_API_KEY = environ["OPENAI_API_KEY"]

experiments = Experiments(MODEL_LOOKUP, host=MODEL_HOSTS, api_key=OPENAI_API_KEY)

SPACE_RE = re.compile(r"\s+")


parser = argparse.ArgumentParser()
parser.add_argument("experiment", choices=ALL_EXPERIMENTS)
args = parser.parse_args()

default_bias = 'A short descriptive phrase for this debate could be "'
experiment_args = experiments.get_experiment_args(args.experiment)
if experiment_args["is_openai"] or "t0" in experiment_args["name"][0]:
    default_bias = None

experiment = experiments.get(args.experiment, bias=default_bias)

try:
    LABEL_GENERATION_PATH = Path(__file__).absolute().parent
except NameError:
    LABEL_GENERATION_PATH = Path(".").absolute()

PROJECT_PATH = LABEL_GENERATION_PATH.parent.parent
DATA_PATH = LABEL_GENERATION_PATH / "data"

DATASET_PATH = PROJECT_PATH / "dataset" / f"default.json"
CLUSTERS_PATH = DATA_PATH / "clusters.json"


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


def get_diff_indexes(arr):
    if len(arr) == 0:
        return []
    diff_arr = np.diff(arr)
    (indices,) = np.where(diff_arr != 0)
    indices += 1
    indices = [0, *(int(e) for e in indices)]
    return indices


def normalize(text):
    return SPACE_RE.sub(" ", text).strip()


def pseudo_join(texts, join_string=" "):
    if not texts:
        return []
    first, *rest = texts
    rest = [f"{join_string}{e}" for e in rest]
    return [first, *rest]


def trim_text(
    client,
    template,
    text,
    max_length=None,
    **client_kwargs,
):
    text = pseudo_join([normalize(e) for e in text])
    if "{input}" in template:
        template_prefix, template_suffix = template.split("{input}")
    else:
        template_prefix, template_suffix = template, ""
    if max_length is not None and max_length > 1:
        model_max_length = max_length
    else:
        model_max_length = (
            client_kwargs.get("model_max_length") or client.meta()["model_max_length"]
        )
        if max_length is not None:
            model_max_length *= max_length
    model_max_length = int(model_max_length)
    size_info = client.count_tokens([template_prefix, *text, template_suffix])
    template_start, *counts, template_end = size_info["counts"]
    max_tokens = (
        model_max_length - template_start - template_end - size_info["num"]["special"]
    )
    if "max_new_tokens" in client_kwargs:
        max_tokens -= client_kwargs["max_new_tokens"]
    cum_tokens = np.cumsum(counts)
    is_less = cum_tokens < max_tokens
    diff_indexes = get_diff_indexes(is_less)[1:]
    if diff_indexes:
        (upper,) = diff_indexes
        selected_text = text[:upper]
    else:
        selected_text = text
    return "".join(selected_text)


try:
    clusters = json.loads(CLUSTERS_PATH.read_text())
except OSError:
    print("clusters.json does not exist, setting up...")
    discussions = read_discussions()
    keys = get_labeled_clusters(discussions, ignore_none=True)
    clusters = {}
    for discussion_key, cluster_key in keys:
        obj = {}
        discussion = discussions[discussion_key]
        cluster = discussion["clusters"][cluster_key]
        sentences = cluster["text"]
        sentences = sorted(sentences, key=lambda x: x["lambda"], reverse=True)
        sentences = [e["text"] for e in sentences]
        gpt3_reference = cluster["gpt3"]["instruct gpt phrase"]
        gpt3_reference = SPACE_RE.sub(" ", gpt3_reference).strip()
        clusters[f"{discussion_key}-{cluster_key}"] = {
            "sentences": sentences,
            "title": discussion["title"],
            "references": {
                "human": cluster["label"],
                "text_davinci_003": gpt3_reference,
            },
        }
    CLUSTERS_PATH.write_text(json.dumps(clusters))
except json.JSONDecodeError:
    print(f"{CLUSTERS_PATH} the file exists but is corrupted")
    exit(1)

max_length = experiment.extra_arguments.get("max_length", 0.8)

client_kwargs = {"max_new_tokens": 64}
if experiment.template.raw().endswith('"'):
    client_kwargs["stopping_strings"] = {"inclusive": ['"']}

trim_kwargs = client_kwargs
if "t0" in experiment_args["name"][0]:
    max_length = 1
    trim_kwargs = {}

# examples = sorted(clusters.items(), key=lambda x: x[0])
# examples = np.random.default_rng(0).choice(examples, 10, replace=False)
# examples = [e for _, e in examples]

# print("++++++++++")
# print(experiment.template.raw())
# print("----------")
# print()
# for example in examples:
#     text = trim_text(
#         experiment.client,
#         experiment.template.raw(),
#         example["sentences"],
#         **client_kwargs,
#         max_length=max_length,
#     )
#     result = (
#         experiment({"input": text}, verbose=True, **client_kwargs)
#         .removeprefix(default_bias)
#         .removesuffix('"')
#     )
#     print("label:", result)


GENERATED_PATH = DATA_PATH / "generated" / f"{experiment.get_name()}.json"
try:
    results = json.loads(GENERATED_PATH.read_text())
except:
    results = {}

results["template"] = experiment.template.raw()
generated = results.setdefault("generated", {})

for i, (key, cluster) in enumerate(clusters.items()):
    print(i)
    sentences = cluster["sentences"]
    if key not in generated:
        text = trim_text(
            experiment.client,
            experiment.template.raw(),
            sentences,
            max_length=max_length,
            **trim_kwargs,
        )
        result = experiment(text, **client_kwargs).strip().removesuffix('"')
        if default_bias:
            result = result.removeprefix(default_bias)
        generated[key] = result
        GENERATED_PATH.write_text(json.dumps(results))
