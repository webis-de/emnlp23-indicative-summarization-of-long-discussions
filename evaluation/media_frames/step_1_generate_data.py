#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

try:
    MEDIA_FRAMES_PATH = Path(__file__).absolute().parent
except NameError:
    MEDIA_FRAMES_PATH = Path(".").absolute()

EXAMPLES_PATH = MEDIA_FRAMES_PATH.parent / "label_generation" / "data" / "examples.json"
DATA_PATH = MEDIA_FRAMES_PATH / "data" / "unlabeled"

PROJECT_PATH = MEDIA_FRAMES_PATH.parent.parent
sys.path.insert(0, str(PROJECT_PATH / "code"))

if DATA_PATH.exists():
    raise ValueError(f"{DATA_PATH} already exists")

PREFIX_RE = re.compile(
    r"^a?\s*\w*\s*(argument|debate|discussion|exploring)s? (of|about|on|against|for)?\s*(the)?",
    flags=re.IGNORECASE,
)
SPACE_RE = re.compile(r"\s+")
FIRST_SENTENCE_RE = re.compile(r".*?[?.!]")


examples = json.loads(EXAMPLES_PATH.read_text())
labels = []
for value in examples.values():
    generated = value["hypotheses"]["gpt3"]
    generated = PREFIX_RE.sub("", generated)
    generated = generated.replace('"', " ")
    generated = generated.strip()
    generated = SPACE_RE.sub(" ", generated)
    generated = "".join([generated[0].upper(), generated[1:]])
    generated = generated.capitalize()
    labels.append(generated)

splits = np.array_split(labels, 2)

frame_names = [
    "economic",
    "capacity_and_resources",
    "morality",
    "fairness_and_equality",
    "legality_constitutionality_and_jurisprudence",
    "policy_prescription_and_evaluation",
    "crime_and_punishment",
    "security_and_defense",
    "health_and_safety",
    "quality_of_life",
    "cultural_identity",
    "public_opinion",
    "political",
    "external_regulation_and_reputation",
]

header = pd.DataFrame(
    dict(zip(["label", "frame1", "frame2", "frame3"], [None] + [frame_names] * 3))
)

DATA_PATH.mkdir(exist_ok=True, parents=True)
for i, split in enumerate(splits, start=1):
    frames = pd.DataFrame({"label": split})
    split_frame = pd.concat([header, frames]).fillna("")
    save_path = DATA_PATH / f"split{i}.csv"
    split_frame.to_csv(save_path, index=False)
