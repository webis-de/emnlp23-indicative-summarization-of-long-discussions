TEXT_DAVINCI_003_TEMPLATE = '''{instruction}

Input: """{input}"""'''

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

VICUNA_TEMPLATE = """{instruction}

USER: {input}

ASSISTANT: """

OASST_TEMPLATE = """<|system|>{instruction}<|endoftext|><|prompter|>{input}<|endoftext|><|assistant|>"""  # v2.5-new

T0PP_TEMPLATE = """{instruction}

Input: {input}"""


TEMPLATES = {
    "gpt-3.5-turbo": {
        "template": "{instruction}",
        "instruction": "direct",
        "max_length": 2048,
    },
    "gpt-4": {
        "template": "{instruction}",
        "instruction": "direct",
        "max_length": 2048,
    },
    "text-davinci-003": {
        "template": TEXT_DAVINCI_003_TEMPLATE,
        "instruction": "direct",
        "max_length": 2048,
    },
    "Alpaca-7B": {
        "template": ALPACA_TEMPLATE,
        "instruction": "direct",
    },
    "Baize-7B": {
        "template": BAIZE_TEMPLATE,
        "instruction": "dialogue",
    },
    "Baize-13B": {
        "template": BAIZE_TEMPLATE,
        "instruction": "dialogue",
    },
    "BLOOM": {
        "template": VICUNA_TEMPLATE,
        "instruction": "dialogue",
        "max_length": 1500,
    },
    "Falcon-40B": {
        "template": VICUNA_TEMPLATE,
        "instruction": "dialogue",
    },
    "Falcon-40B-Instruct": {
        "template": VICUNA_TEMPLATE,
        "instruction": "dialogue",
    },
    "GPT-NeoX": {
        "template": VICUNA_TEMPLATE,
        "instruction": "dialogue",
    },
    "LLaMA-30B": {
        "template": VICUNA_TEMPLATE,
        "instruction": "dialogue",
    },
    "LLaMA-30B-SuperCOT": {
        "template": ALPACA_TEMPLATE,
        "instruction": "direct",
    },
    "LLaMA-65B": {
        "template": VICUNA_TEMPLATE,
        "instruction": "dialogue",
        "max_length": 1500,
    },
    "OASST": {
        "template": OASST_TEMPLATE,
        "instruction": "direct",
    },
    "Pythia": {
        "template": OASST_TEMPLATE,
        "instruction": "direct",
    },
    "OPT-66B": {
        "template": VICUNA_TEMPLATE,
        "instruction": "dialogue",
    },
    "T0++": {
        "template": T0PP_TEMPLATE,
        "instruction": "direct",
    },
    "Vicuna-7B": {
        "template": VICUNA_TEMPLATE,
        "instruction": "dialogue",
    },
    "Vicuna-13B": {
        "template": VICUNA_TEMPLATE,
        "instruction": "dialogue",
    },
}
