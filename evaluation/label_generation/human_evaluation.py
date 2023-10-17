#!/usr/bin/env python

import json
from collections import defaultdict
from pathlib import Path

import kendall_w.kendall_w as kw
import numpy as np
import pandas as pd

try:
    path = Path(__file__).resolve().parent
except NameError:
    path = Path("./evaluation/label_generation").resolve()
path = path / "data" / "users"

files = list(path.glob("*.json"))

results = []
for file in files:
    data = json.loads(file.read_text())
    if len(data) == 300:
        results.append(data)

res = [pd.Series(e) for e in results]
dat = pd.concat(res, axis=1)


def compute_kendall_w(rankings):
    converted = defaultdict(list)
    for ranking in rankings:
        for i, model in enumerate(ranking, start=1):
            converted[model].append(i)
    converted = list(converted.values())
    return kw.compute_w(converted)


def group_scores(ranking):
    reversed_ranking = defaultdict(list)
    for key, value in ranking.items():
        reversed_ranking[value].append(key)
    grouped = {" ".join(sorted(value)): key for key, value in reversed_ranking.items()}
    return grouped


def mrr(rankings, k=60):
    rank_maps = [
        {doc: rank for rank, doc in enumerate(ranking, start=1)} for ranking in rankings
    ]
    documents = {doc for rm in rank_maps for doc in rm}
    new_ranks = {doc: sum([1 / (k + rm[doc]) for rm in rank_maps]) for doc in documents}
    scores = group_scores(new_ranks)
    fused = [e for e, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]
    return fused


fused = dat.apply(lambda x: mrr(x, k=60), axis=1)

all_ranks = fused.tolist()

expanded_rankings = []
for ranking in all_ranks:
    expanded_ranking = {}
    for docs in ranking:
        current_rank = len(expanded_ranking) + 1
        for doc in docs.split(" "):
            expanded_ranking[doc] = current_rank
    expanded_rankings.append(expanded_ranking)

ranking_frame = pd.DataFrame(expanded_rankings)
averaged = ranking_frame.mean(axis=0)
averaged.name = "score"
print(averaged.to_markdown())
print()

W = np.array([compute_kendall_w(rankings) for _, rankings in dat.iterrows()]).mean()
print(f"Kendall W: {W:.3f}")
