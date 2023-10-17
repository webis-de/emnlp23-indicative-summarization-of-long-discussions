#!/usr/bin/env python3

import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

from sbert import SBERT

LABEL_GENERATION_PATH = Path(__file__).absolute().parent
DATA_PATH = LABEL_GENERATION_PATH / "data"
PROJECT_PATH = LABEL_GENERATION_PATH.parent.parent

def normalize(arr):
    return arr / np.linalg.norm(arr, axis=1)[..., None]


SMALLEST_FLOAT = np.finfo("float32").smallest_subnormal


def cos_sim(v1, v2=None, *, full=False, lower_clip=False):
    v1 = normalize(v1)
    if v2 is not None:
        v2 = normalize(v2)
        if full:
            similarity = v1 @ v2.T
        else:
            similarity = (v1 * v2).sum(axis=1)
    else:
        similarity = v1 @ v1.T
    lower = SMALLEST_FLOAT if lower_clip else -1.0
    similarity = np.clip(similarity, lower, 1.0)
    return similarity


rng = np.random.default_rng()


DATASET_PATH = PROJECT_PATH / "dataset" / f"default.json"
EXAMPLES_PATH = DATA_PATH / "examples.json"

PREFIX_RE = re.compile(
    r"^a?\s*\w*\s*(argument|debate|discussion|exploring)s? (of|about|on|against|for)?\s*(the)?",
    flags=re.IGNORECASE,
)
SPACE_RE = re.compile(r"\s+")
FIRST_SENTENCE_RE = re.compile(r".*?[?.!]")


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


model = SBERT(model="performance")

EXAMPLES_PATH.parent.mkdir(exist_ok=True, parents=True)
discussions = read_discussions()
keys = get_labeled_clusters(discussions, ignore_none=True)
best_prompts = {
    "t0_output_type": "title",
    "bloom": "dialog title",
    "gptneox": "qa discussion topic",
    "opt66": "qa topic",
    "gpt3": "instruct gpt phrase",
}
examples = {}
for discussion_key, cluster_key in keys:
    obj = {}
    discussion = discussions[discussion_key]
    cluster = discussion["clusters"][cluster_key]
    obj["discussion"] = discussion_key
    obj["cluster"] = cluster_key
    obj["title"] = discussion["title"]
    obj["reference"] = cluster["label"]
    hypotheses = {}
    for model_name, sub_key in best_prompts.items():
        generated = cluster[model_name][sub_key]
        generated = PREFIX_RE.sub("", generated)
        generated = generated.replace('"', " ")
        if len(generated.split()) > 15:
            sentences = FIRST_SENTENCE_RE.findall(generated)
            if sentences:
                generated = sentences[0]
        generated = generated.strip()
        generated = SPACE_RE.sub(" ", generated)
        generated = generated.capitalize()
        if generated and generated[-1] not in ".?!":
            generated += "."
        outname = model_name
        if "t0" in outname:
            outname = "t0"
        hypotheses[outname] = generated
    reverse_hyps = defaultdict(list)
    for key, value in hypotheses.items():
        reverse_hyps[value].append(key)
    hypotheses = {" ".join(sorted(value)): key for key, value in reverse_hyps.items()}
    obj["hypotheses"] = hypotheses
    texts = defaultdict(lambda: float("-inf"))
    for e in cluster["text"]:
        text = e["text"]
        lambda_ = e["lambda"]
        texts[text] = max(texts[text], lambda_)
    max_lambda = max(e for e in texts.values())
    sentences = [text for text, lambda_ in texts.items() if lambda_ == max_lambda]
    key_sentences = list(hypotheses.values()) + [cluster["label"]]
    sentence_embeddings = model(sentences)
    key_embeddings = model(key_sentences)
    sims = cos_sim(sentence_embeddings, key_embeddings, full=True)
    scores = sims.mean(axis=1)
    sentences_with_score = sorted(
        zip(scores, sentences), key=lambda x: x[0], reverse=True
    )
    top_sentences = [v for _, v in sentences_with_score]
    top_sentences = top_sentences[:5]
    rest_sentences = [text for text in texts.keys() if text not in top_sentences]
    rng.shuffle(rest_sentences)
    random_sentences = rest_sentences[:5]
    obj["top_sentences"] = top_sentences
    obj["random_sentences"] = random_sentences
    examples[f"{discussion_key}-{cluster_key}"] = obj
EXAMPLES_PATH.write_text(json.dumps(examples))
