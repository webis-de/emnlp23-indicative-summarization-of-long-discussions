#!/usr/bin/env python

import argparse
import re

from config import MODEL_HOSTS, OPENAI_API_KEY
from pipeline import Pipeline, Summarizer
from templates import TEMPLATES as _TEMPLATES
from util.static import load_static, write_static, SOURCES


TEMPLATES = {
    **_TEMPLATES,
    "T0++": {
        "template": "Read the following context and answer the question.\nContext:\n{input}\nQuestion: What is the title of the text?\nAnswer:",
    },
    "BLOOM": {
        "template": 'AI assistant: I am an expert AI assistant and I am very good in identifying titles of debates.\nDEBATE START\n{input}\nDEBATE END\nAI assistant: The title of the debate between the two participants is "',
        "max_length": 1500,
    },
    "GPT-NeoX": {
        "template": 'DISCUSSION START\n{input}\nDISCUSSION END\nQ: What is the topic of the discussion?\nA: The topic of the discussion is "',
    },
    "OPT-66B": {
        "template": 'DEBATE START\n{input}\nDEBATE END\nQ: What is the topic of the debate?\nA: The topic of the debate is "',
    },
}

bias = 'A short descriptive phrase for this debate could be "'
stopping_strings = {"exclusive": ['"']}
postprocess = lambda x: x.strip().strip('"')


NON_ALPHANUM_RE = re.compile(r"[^a-z0-9_]")


def to_short_name(model):
    return NON_ALPHANUM_RE.sub("", model.lower().replace("-", "_").replace("+", "p"))


LOWER_LABEL_TEMPLATES = {to_short_name(key): value for key, value in TEMPLATES.items()}

LABEL_TEMPLATES = {
    key: value
    if any(
        e in key.lower()
        for e in ["gpt_35", "gpt_4", "text_davinci", "t0", "opt", "neox", "bloom"]
    )
    else {
        "bias": bias,
        "client_kwargs": {"stopping_strings": stopping_strings},
        **value,
    }
    for key, value in LOWER_LABEL_TEMPLATES.items()
}

LOWER_FRAME_TEMPLATES = {to_short_name(key): value for key, value in _TEMPLATES.items()}

FRAME_TEMPLATES = {
    key: value
    if any(
        e in key.lower()
        for e in [
            "supercot",
            "pythia",
            "oasst",
            "alpaca",
            "baize",
            "vicuna",
            "gpt_35",
            "gpt_4",
            "text_davinci",
            "t0",
        ]
    )
    else {
        "bias": '["',
        "client_kwargs": {"stopping_strings": {"exclusive": ['"]']}},
        **value,
    }
    for key, value in LOWER_FRAME_TEMPLATES.items()
}

MODEL_MAP = {to_short_name(key): key for key in TEMPLATES.keys()}
MODEL_MAP.update(
    {
        "t0": MODEL_MAP["t0pp"],
        "opt66": MODEL_MAP["opt_66b"],
        "gptneox": MODEL_MAP["gpt_neox"],
    }
)

parser = argparse.ArgumentParser()
parser.add_argument("model", choices=set(MODEL_MAP.keys()))
args = parser.parse_args()

model = MODEL_MAP[args.model]


def rename_dict(rename_map, data):
    did_rename = False
    for key in list(data.keys()):
        if key in rename_map:
            data[rename_map[key]] = data.pop(key)
            did_rename = True
    return did_rename


class Static:
    def __init__(self, model, ignore=[]):
        self.static = load_static()
        for model in ignore:
            for value in self.static.values():
                for e in ["labels", "frames"]:
                    if model in value[e]:
                        print("deleting")
                        del value[e][model]
        self.pipeline = Pipeline()
        self.summarizer = Summarizer(
            label_model=model,
            frame_model=model,
            host=MODEL_HOSTS,
            api_key=OPENAI_API_KEY,
        )

    def write(self):
        write_static(self.static)

    def fetch(self):
        for url in SOURCES:
            if url not in self.static:
                print(f"fetching {url} ...")
                self.static[url] = self.pipeline(url)
                self.write()

    def label(self):
        model = self.summarizer.label_model
        for key, tree in self.static.items():
            if model not in tree["labels"]:
                print(f"labeling {key} ...")
                self.summarizer.label(tree, templates=LABEL_TEMPLATES)
            self.write()

    def frame(self):
        model = self.summarizer.frame_model
        for key, tree in self.static.items():
            if model not in tree.get("frames", {}).get(model, {}):
                print(f"framing {key} ...")
                self.summarizer.frame(tree, templates=FRAME_TEMPLATES)
            self.write()

    def rename(self, rename_map):
        did_rename = False
        for tree in self.static.values():
            did_rename = rename_dict(rename_map, tree["labels"]) | did_rename
            did_rename = rename_dict(rename_map, tree["frames"]) | did_rename
            for value in tree["frames"].values():
                did_rename = rename_dict(rename_map, value) | did_rename
        if did_rename:
            self.write()


static = Static(model, ignore=[])

static.fetch()
static.label()
static.frame()
static.rename(MODEL_MAP)
