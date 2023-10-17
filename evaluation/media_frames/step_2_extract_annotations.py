#!/usr/bin/env python3

import json
from pathlib import Path

import numpy as np
import pandas as pd

try:
    MEDIA_FRAMES_PATH = Path(__file__).absolute().parent
except NameError:
    MEDIA_FRAMES_PATH = Path(".").absolute()

# move the labeled splits into this folder
RESULTS_PATH = MEDIA_FRAMES_PATH / "data" / "labeled"

PROJECT_PATH = MEDIA_FRAMES_PATH.parent.parent

frames = []
for path in sorted(RESULTS_PATH.glob("*.csv")):
    frame = pd.read_csv(path)
    frame = frame[~frame["label"].isna()]
    frames.append(frame)

df = pd.concat(frames).reset_index(drop=True)
df = df[~df["frame1"].isna()]
frame_names = sorted(df["frame1"].value_counts().index)
rng = np.random.default_rng(0)
examples = {}
for frame_name in frame_names:
    selector = df["frame1"] == frame_name
    indexes = df[selector].index
    selected = rng.choice(indexes, 3, replace=False)
    examples[frame_name] = df.loc[selected]["label"].tolist()
    df = df.drop(index=selected)
annotations = [
    {"label": row["label"], "frames": row[1:][~row[1:].isna()].tolist()}
    for _, row in df.iterrows()
]

result = {"examples": examples, "annotations": annotations}

ANNOTATIONS_PATH = RESULTS_PATH / "annotations.json"
if ANNOTATIONS_PATH.exists():
    raise ValueError(f"{ANNOTATIONS_PATH} already exists")
ANNOTATIONS_PATH.write_text(json.dumps(result, ensure_ascii=True))
