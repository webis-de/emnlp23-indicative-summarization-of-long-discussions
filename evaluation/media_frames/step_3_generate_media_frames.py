#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

from experiment_definitions import ALL_EXPERIMENTS, experiments
from frames import INSTRUCTION_ARGUMENTS

parser = argparse.ArgumentParser()
parser.add_argument("experiment", choices=ALL_EXPERIMENTS)
args = parser.parse_args()

experiment = experiments.get(args.experiment)


try:
    MEDIA_FRAMES_PATH = Path(__file__).absolute().parent
except NameError:
    MEDIA_FRAMES_PATH = Path(".").absolute()

DATA_PATH = MEDIA_FRAMES_PATH / "data"
ANNOTATIONS_PATH = DATA_PATH / "labeled" / "annotations.json"
annotations = json.loads(ANNOTATIONS_PATH.read_text())["annotations"]

# print("++++++++++")
# print(experiment.template.raw())
# print("----------")
# print()
# for example in annotations[:10]:
#     result = experiment(
#         example["label"],
#         INSTRUCTION_ARGUMENTS["zero_shot_extreme"],
#         verbose=True,
#         max_new_tokens=64,
#     )
#     print("media frames:", result)
#     print()
# exit(0)

GENERATED_PATH = DATA_PATH / "generated" / f"{experiment.get_name()}.json"
try:
    results = json.loads(GENERATED_PATH.read_text())
except:
    results = {}

results["template"] = experiment.template.raw()
generated = results.setdefault("generated", {})


for i, annotation in enumerate(annotations):
    print(i)
    label = annotation["label"]
    frames = annotation["frames"]
    if label not in generated:
        generated[label] = {"frames": frames}
    data = generated[label]
    for experiment_type, instruction_arguments in INSTRUCTION_ARGUMENTS.items():
        if experiment_type in experiment.skip:
            continue
        if experiment_type not in data:
            data[experiment_type] = (
                experiment(label, instruction_arguments, ensure_complete=False)
                .strip()
                .removesuffix('"')
            )
            GENERATED_PATH.write_text(json.dumps(results))
