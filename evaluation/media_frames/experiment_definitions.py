import re
import sys
from os import environ
from pathlib import Path

import dotenv

language_models_path = str(Path(__file__).parent.parent.parent / "language_models")
sys.path.insert(0, language_models_path)

from experiment_tools import Experiments

# INSTRUCTIONS -----------------------------------
DESCRIPTIVE_INSTRUCTION = """A chat between a curious user and an artificial intelligence assistant.
The assistant knows all media frames as defined in the work from {authors}: {frames}
The assistant answers with three of these media frames corresponding to the user's text, in order of importance."""

DESCRIPTIVE_INSTRUCTION_WITHOUT_AUTHORS = """A chat between a curious user and an artificial intelligence assistant.
The assistant knows all the following media frames: {frames}
The assistant answers with three of these media frames corresponding to the user's text, in order of importance."""

INSTRUCT_INSTRUCTION = """The following {input_type} contains all available media frames as defined in the work from {authors}: {frames}
For every input, you answer with three of these media frames corresponding to that input, in order of importance."""

INSTRUCT_INSTRUCTION_WITHOUT_AUTHORS = """The following {input_type} contains all the available media frames: {frames}
For every input, you answer with three of these media frames corresponding to that input, in order of importance."""

LIST_BIAS = '["'  # ]
# INSTRUCTIONS END -------------------------------

REMOVE_NON_ALPANUM = re.compile(r"[^a-z0-9_]")

TEXT_DAVINCI_003_TEMPLATE = '''{instruction}

Input: """{input}"""

Answer: '''

# source: https://github.com/tatsu-lab/stanford_alpaca#data-release
# source: https://github.com/oobabooga/text-generation-webui/blob/main/prompts/Alpaca-with-Input.txt

ALPACA_TEMPLATE = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input}

### Response:
"""

BAIZE_TEMPLATE = """{instruction}
[|Human|]{input}
[|AI|]"""


BLOOM_TEMPALTE = """{instruction}

USER: What are the media frames of the following text?: {input}

ASSISTANT: The media frames of this text are """

# source: https://github.com/lm-sys/FastChat/blob/main/fastchat/conversation.py

VICUNA_TEMPLATE = """{instruction}

USER: {input}

ASSISTANT: """

GPT_NEOX_TEMPLATE = """{instruction}

USER: What are the media frames of the following text?: "{input}"

ASSISTANT: The three most important media frames are """

# source: https://github.com/lm-sys/FastChat/blob/main/fastchat/conversation.py

# OASST_TEMPLATE = """<prefix>{instruction}</prefix><human>{input}<bot>"""  # v2
# OASST_TEMPLATE = """<|prefix_begin|>{instruction}<|prefix_end|><|prompter|>{input}<|endoftext|><|assistant|>"""  # v2.5-old
OASST_TEMPLATE = """<|system|>{instruction}<|endoftext|><|prompter|>{input}<|endoftext|><|assistant|>"""  # v2.5-new


OPT66_TEMPLATE = """{instruction}

USER: What are the media frames of the following text?: {input}

ASSISTANT: The media frames of this text are: """

T0PP_TEMPLATE = """{instruction}

Input: {input}

Answer:"""


EXPERIMENTS = {
    "GPT-3.5-Turbo": {
        None: {
            "template": "{instruction}",
            "instruction": INSTRUCT_INSTRUCTION,
        },
        "without_authors": {
            "template": "{instruction}",
            "instruction": INSTRUCT_INSTRUCTION_WITHOUT_AUTHORS,
        },
    },
    "GPT-4": {
        None: {
            "template": "{instruction}",
            "instruction": INSTRUCT_INSTRUCTION,
        }
    },
    "Text-Davinci-003": {
        None: {
            "template": TEXT_DAVINCI_003_TEMPLATE,
            "instruction": INSTRUCT_INSTRUCTION,
        }
    },
    "Alpaca-7B": {
        None: {
            "template": ALPACA_TEMPLATE,
            "instruction": INSTRUCT_INSTRUCTION,
        }
    },
    "Baize-7B": {
        None: {
            "template": BAIZE_TEMPLATE,
            "instruction": DESCRIPTIVE_INSTRUCTION,
        }
    },
    "Baize-13B": {
        None: {
            "template": BAIZE_TEMPLATE,
            "instruction": DESCRIPTIVE_INSTRUCTION,
        }
    },
    "BLOOM": {
        None: {
            "template": BLOOM_TEMPALTE,
            "instruction": DESCRIPTIVE_INSTRUCTION,
            "bias": LIST_BIAS,
            "client_kwargs": {
                "max_new_tokens": 64,
            },
            "skip": ["few_shot"],
        }
    },
    "Falcon-40B": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DESCRIPTIVE_INSTRUCTION,
            "bias": LIST_BIAS,
        },
        "without_authors": {
            "template": VICUNA_TEMPLATE,
            "instruction": DESCRIPTIVE_INSTRUCTION_WITHOUT_AUTHORS,
            "bias": LIST_BIAS,
        },
    },
    "Falcon-40B-Instruct": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DESCRIPTIVE_INSTRUCTION,
            "bias": LIST_BIAS,
        }
    },
    "GPT-NeoX": {
        None: {
            "template": GPT_NEOX_TEMPLATE,
            "instruction": DESCRIPTIVE_INSTRUCTION,
            "bias": LIST_BIAS,
        }
    },
    "LLaMA-30B": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DESCRIPTIVE_INSTRUCTION,
            "bias": LIST_BIAS,
        }
    },
    "LLaMA-30B-SuperCOT": {
        None: {
            "template": ALPACA_TEMPLATE,
            "instruction": INSTRUCT_INSTRUCTION,
        }
    },
    "LLaMA-65B": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DESCRIPTIVE_INSTRUCTION,
            "bias": LIST_BIAS,
            "skip": ["few_shot"],
        },
        "without_authors": {
            "template": VICUNA_TEMPLATE,
            "instruction": DESCRIPTIVE_INSTRUCTION_WITHOUT_AUTHORS,
            "bias": LIST_BIAS,
            "skip": ["few_shot"],
        },
    },
    "OASST": {
        None: {
            "template": OASST_TEMPLATE,
            "instruction": INSTRUCT_INSTRUCTION,
        }
    },
    "Pythia": {
        None: {
            "template": OASST_TEMPLATE,
            "instruction": INSTRUCT_INSTRUCTION,
        }
    },
    "OPT-66B": {
        None: {
            "template": OPT66_TEMPLATE,
            "instruction": DESCRIPTIVE_INSTRUCTION,
            "bias": LIST_BIAS,
            "skip": ["few_shot"],
        }
    },
    "T0++": {
        None: {
            "template": T0PP_TEMPLATE,
            "instruction": INSTRUCT_INSTRUCTION,
        }
    },
    "Vicuna-7B": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DESCRIPTIVE_INSTRUCTION,
        }
    },
    "Vicuna-13B": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DESCRIPTIVE_INSTRUCTION,
        }
    },
}


MODEL_LOOKUP = {
    REMOVE_NON_ALPANUM.sub("", model.lower().replace("-", "_").replace("+", "p")): {
        "model": model,
        "experiments": experiments,
    }
    for model, experiments in EXPERIMENTS.items()
}

ALL_EXPERIMENTS = [
    short_model + (f".{experiment}" if experiment else "")
    for short_model, value in MODEL_LOOKUP.items()
    for experiment in value["experiments"].keys()
]

dotenv.load_dotenv()

MODEL_HOSTS = environ["MODEL_HOSTS"].split()
OPENAI_API_KEY = environ["OPENAI_API_KEY"]

experiments = Experiments(MODEL_LOOKUP, host=MODEL_HOSTS, api_key=OPENAI_API_KEY)
