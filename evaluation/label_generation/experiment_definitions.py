import re

# INSTRUCTIONS -----------------------------------
DIALOGUE_INSTRUCTION = """A chat between a curious user and an artificial intelligence assistant.
The user presents a debate and the assistant generates a single descriptive phrase that describes the debate in very simple language, without talking about the debate or the author."""

DIRECT_INSTRUCTION = """Every input is the content of a debate. For every input, you generate a single descriptive phrase that describes that input in very simple language, without talking about the debate or the author."""
# INSTRUCTIONS END -------------------------------

NON_ALPHANUM_RE = re.compile(r"[^a-z0-9_]")

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


# source: https://github.com/lm-sys/FastChat/blob/main/fastchat/conversation.py

VICUNA_TEMPLATE = """{instruction}

USER: {input}

ASSISTANT: """

# source: https://github.com/lm-sys/FastChat/blob/main/fastchat/conversation.py

# OASST_TEMPLATE = """<prefix>{instruction}</prefix><human>{input}<bot>"""  # v2
# OASST_TEMPLATE = """<|prefix_begin|>{instruction}<|prefix_end|><|prompter|>{input}<|endoftext|><|assistant|>"""  # v2.5-old
OASST_TEMPLATE = """<|system|>{instruction}<|endoftext|><|prompter|>{input}<|endoftext|><|assistant|>"""  # v2.5-new


T0PP_TEMPLATE = """{instruction}

Input: {input}

Descriptive phrase:"""


EXPERIMENTS = {
    "GPT-3.5-Turbo": {
        None: {
            "template": "{instruction}",
            "instruction": DIRECT_INSTRUCTION,
            "extra_arguments": {"max_length": 2048},
        },
    },
    "GPT-4": {
        None: {
            "template": "{instruction}",
            "instruction": DIRECT_INSTRUCTION,
            "extra_arguments": {"max_length": 2048},
        }
    },
    "Text-Davinci-003": {
        None: {
            "template": TEXT_DAVINCI_003_TEMPLATE,
            "instruction": DIRECT_INSTRUCTION,
            "extra_arguments": {"max_length": 2048},
        }
    },
    "Alpaca-7B": {
        None: {
            "template": ALPACA_TEMPLATE,
            "instruction": DIRECT_INSTRUCTION,
        }
    },
    "Baize-7B": {
        None: {
            "template": BAIZE_TEMPLATE,
            "instruction": DIALOGUE_INSTRUCTION,
        }
    },
    "Baize-13B": {
        None: {
            "template": BAIZE_TEMPLATE,
            "instruction": DIALOGUE_INSTRUCTION,
        }
    },
    "BLOOM": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DIALOGUE_INSTRUCTION,
        }
    },
    "Falcon-40B": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DIALOGUE_INSTRUCTION,
        },
    },
    "Falcon-40B-Instruct": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DIALOGUE_INSTRUCTION,
        }
    },
    "GPT-NeoX": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DIALOGUE_INSTRUCTION,
        }
    },
    "LLaMA-30B": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DIALOGUE_INSTRUCTION,
        }
    },
    "LLaMA-30B-SuperCOT": {
        None: {
            "template": ALPACA_TEMPLATE,
            "instruction": DIRECT_INSTRUCTION,
        }
    },
    "LLaMA-65B": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DIALOGUE_INSTRUCTION,
            "extra_arguments": {"max_length": 1400},
        },
    },
    "OASST": {
        None: {
            "template": OASST_TEMPLATE,
            "instruction": DIRECT_INSTRUCTION,
        }
    },
    "Pythia": {
        None: {
            "template": OASST_TEMPLATE,
            "instruction": DIRECT_INSTRUCTION,
        }
    },
    "OPT-66B": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DIALOGUE_INSTRUCTION,
            "extra_arguments": {"max_length": 1400},
        }
    },
    "T0++": {
        None: {
            "template": T0PP_TEMPLATE,
            "instruction": DIRECT_INSTRUCTION,
        }
    },
    "Vicuna-7B": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DIALOGUE_INSTRUCTION,
        }
    },
    "Vicuna-13B": {
        None: {
            "template": VICUNA_TEMPLATE,
            "instruction": DIALOGUE_INSTRUCTION,
        }
    },
}


MODEL_LOOKUP = {
    NON_ALPHANUM_RE.sub("", model.lower().replace("-", "_").replace("+", "p")): {
        "model": model,
        "experiments": experiments,
    }
    for model, experiments in EXPERIMENTS.items()
}

RENAME_MAP = {key: value["model"] for key, value in MODEL_LOOKUP.items()}

ALL_EXPERIMENTS = [
    short_model + (f".{experiment}" if experiment else "")
    for short_model, value in MODEL_LOOKUP.items()
    for experiment in value["experiments"].keys()
]
