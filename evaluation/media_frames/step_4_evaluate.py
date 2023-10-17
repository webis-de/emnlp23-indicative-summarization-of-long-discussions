#!/usr/bin/env python3

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

from experiment_definitions import MODEL_LOOKUP


def get_diff_indexes(arr, add_end=False):
    if len(arr) == 0:
        return []
    counter = 0
    all_keys = {}
    new_arr = []
    for e in arr:
        if e not in all_keys:
            all_keys[e] = counter
            counter += 1
        new_arr.append(all_keys[e])
    if add_end:
        new_arr.append(counter)
    diff_arr = np.diff(new_arr)
    (indices,) = np.where(diff_arr != 0)
    indices += 1
    indices = [0, *(int(e) for e in indices)]
    return indices


def ltext(text, bold=True, ttfamily=False):
    if not text:
        return text
    text = text.replace("_", r"\_")
    if ttfamily:
        text = rf"\ttfamily{{{text}}}"
    if bold:
        text = rf"\textbf{{{text}}}"
    return text


def to_latex(df, precision):
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.map(lambda x: tuple(ltext(e) for e in x))
        first = df.columns.get_level_values(0)
        diffs = get_diff_indexes(first, add_end=True)
        spans = []
        for start, end in zip(diffs, diffs[1:]):
            start = start + 1
            if start != end:
                spans.append(rf"\cmidrule(lr){{{start}-{end}}}")
        extra = "".join(spans)
    else:
        df.columns = df.columns.map(lambda x: ltext(x))
        extra = None
    df.iloc[:, 0] = df.iloc[:, 0].map(lambda x: ltext(x, ttfamily=True))
    text = df.to_latex(
        index=False,
        float_format=f"%.{precision}f",
        bold_rows=True,
        na_rep="--",
        multicolumn_format="c",
    ).strip()
    if extra:
        lines = text.splitlines()
        lines.insert(3, extra)
        text = "\n".join(lines)
    return f"```latex\n{text}\n```"


STYLES = {
    "markdown": lambda x, _: x.to_markdown(index=False),
    "latex": to_latex,
    "csv": lambda x, precision: x.to_csv(index=False, float_format=f"%.{precision}f"),
}

NUMBERS = ["all", "absolute", "percentage"]


parser = argparse.ArgumentParser()
parser.add_argument("--style", default="markdown", choices=list(STYLES.keys()))
parser.add_argument("--numbers", default="percentage", choices=NUMBERS)
parser.add_argument("--combine", action="store_true")
parser.add_argument("--show-all", action="store_true")
parser.add_argument("--transpose", action="store_true")
parser.add_argument("--all-top", action="store_true")
parser.add_argument("--experiment", default=None)
parser.add_argument("--model", default=None)
parser.add_argument("--default-name", default=None)
args = parser.parse_args()

style = args.style
combine = args.combine
numbers = args.numbers
show_all = args.show_all
transpose = args.transpose
sub_experiment_string = args.experiment
all_top = args.all_top
default_name = args.default_name
model_should_contain = args.model and args.model.lower().split(",")

frame_names = {
    "economic": ["financial"],
    "capacity and resources": [],
    "morality": ["moral", "ethic"],
    "fairness and equality": [],
    "legality, constitutionality and jurisprudence": ["legality", "legal"],
    "policy prescription and evaluation": [],
    "crime and punishment": [],
    "security and defense": ["security"],
    "health and safety": [
        "safety and danger",
        "healthcare",
        "safety",
        "health",
        "medicine",
    ],
    "quality of life": [],
    "cultural identity": ["cultural"],
    "public opinion": [],
    "political": ["politics"],
    "external regulation and reputation": [],
}

alt_frame_names = {}
for frame, alt_frames in frame_names.items():
    for alt_frame in alt_frames:
        alt_frame_names[alt_frame] = frame

new_frames = [
    "environmental",
    "technology and innovation",
    "emotional valence",
    "professionalism",
    "sport",
    "gender",
    "social norms",
    "education",
    "immigration",
    "superheroes",
    "abilities",
    "science and technology",
    "religion and belief",
    "scientific rigor",
]

frame_regex = re.compile("|".join(frame_names))
alt_frame_regex = re.compile("|".join(alt_frame_names))
left_regex = re.compile(r'^[ \n\t,"]*$')


def parse(labels):
    left = labels.lower()
    parsed = frame_regex.findall(left)
    left = frame_regex.sub("", left)
    alt_frames = alt_frame_regex.findall(left)
    parsed.extend([alt_frame_names[alt_frame] for alt_frame in alt_frames])
    left = alt_frame_regex.sub("", left)
    parsed = [e.replace(",", "").replace(" ", "_") for e in parsed]
    unique = []
    for e in parsed:
        if e not in unique:
            unique.append(e)
    return unique


ALIASES = {
    "zero_shot_extreme": "Zero-Shot (no description)",
    "zero_shot_simple": "Zero-Shot (short description)",
    "zero_shot": "Zero-Shot (long description)",
    "few_shot": "Few-Shot",
}

try:
    MEDIA_FRAMES_PATH = Path(__file__).absolute().parent
except NameError:
    MEDIA_FRAMES_PATH = Path(".").absolute()

GENERATED_PATH = MEDIA_FRAMES_PATH / "data" / "generated"
FILES = list(GENERATED_PATH.glob("*.json"))


def render_results(results, transpose=True, precision=2):
    df = pd.DataFrame(results)
    if len(df.columns) == 0:
        return
    df = df.sort_index()
    if transpose:
        df = df.T
    sub_columns = [e.replace(" - ", ":") for e in df.columns]
    if all(":" in e for e in sub_columns):
        df.columns = pd.MultiIndex.from_tuples(
            [column.split(":") for column in sub_columns]
        )
    df = df.reset_index(names=["experiment"])
    print(STYLES[style](df, precision))


def final_name(model_name, sub_experiment):
    if sub_experiment is None:
        sub_experiment = default_name
    if sub_experiment:
        return f"{model_name} - {sub_experiment.replace('_', ' ')}"
    return model_name


def print_results(model_name, experiment, results, precision=2):
    header = final_name(model_name, experiment)
    print()
    print(f"## {header}")
    print()
    if numbers == "all":
        for value in results.values():
            render_results(value, precision=precision)
            print()
    else:
        render_results(results[numbers], precision=precision)


all_results = {}

for file in FILES:
    generated = json.loads(file.read_text())
    if "generated" in generated:
        generated = generated["generated"]

    experiments = defaultdict(list)
    for label, value in generated.items():
        value = value.copy()
        frames = value.pop("frames")
        for experiment_type, hypotheses in value.items():
            experiments[experiment_type].append([frames, parse(hypotheses)])

    def has_overlap(references, hypotheses, top=None):
        if top is not None:
            hypotheses = hypotheses[:top]
        return bool(set(references) & set(hypotheses))

    results_absolute = {}
    for experiment_type, experiment in experiments.items():
        experiment_results = defaultdict(int)
        for references, hypotheses in experiment:
            for i in [1, 2, 3]:
                experiment_results[f"top {i}"] += has_overlap(references, hypotheses, i)
        results_absolute[ALIASES[experiment_type]] = dict(experiment_results)

    num_examples = len(generated)
    results_percentage = {
        experiment: {
            key: round(value / num_examples * 100, 1)
            for key, value in experiment_definition.items()
        }
        for experiment, experiment_definition in results_absolute.items()
    }

    splitted = file.stem.split(".")
    short_model = splitted[0]
    sub_experiment = ".".join(splitted[1:]) or None
    name = short_model

    clean_model_name = MODEL_LOOKUP[short_model]["model"]

    should_show = True
    if sub_experiment_string is None:
        if sub_experiment is not None:
            should_show = False
    else:
        if sub_experiment is None or not sub_experiment in sub_experiment_string:
            should_show = False

    if model_should_contain is not None:
        should_show = any(
            e in clean_model_name.lower() + " " or e in short_model.lower() + " "
            for e in model_should_contain
        )

    if show_all or should_show:
        all_results[(clean_model_name, sub_experiment)] = {
            "absolute": results_absolute,
            "percentage": results_percentage,
        }


def combine_results(results, key):
    combined = defaultdict(lambda: {})
    for (model_name, sub_experiment), value in results.items():
        for experiment, experiment_results in value[key].items():
            if all_top:
                for top_key, value in experiment_results.items():
                    combined[f"{experiment}:{top_key}"][
                        final_name(model_name, sub_experiment)
                    ] = value
            else:
                combined[experiment][
                    final_name(model_name, sub_experiment)
                ] = experiment_results["top 1"]
    render_results(combined, transpose=args.transpose)


if combine:
    if numbers == "all":
        for value in ["absolute", "percentage"]:
            combine_results(all_results, value)
            print()
    else:
        combine_results(all_results, numbers)
else:
    for (model_name, experiment), results in all_results.items():
        print_results(model_name, experiment, results, precision=1)
