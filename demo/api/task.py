import re

from clean import clean
from clients.gpt_client import OpenAIClient
from template import Template
from templates import TEMPLATES
from util.frames import parse_frames
from util.trim import trim_text

NON_ALPHANUM_RE = re.compile(r"[^a-z0-9_]")


def to_short_name(model):
    return NON_ALPHANUM_RE.sub("", model.lower().replace("-", "_").replace("+", "p"))


LOWER_TEMPLATES = {to_short_name(key): value for key, value in TEMPLATES.items()}


class TaskBase:
    def __init__(
        self,
        client,
        *,
        templates=LOWER_TEMPLATES,
        direct_instruction=None,
        dialogue_instruction=None,
        max_new_tokens=64,
    ):
        self.client = client
        self.is_chat = hasattr(client, "is_chat") and client.is_chat
        self.info = templates[to_short_name(client.model)].copy()
        instruction_type = (
            self.info["instruction"] if "instruction" in self.info else None
        )
        self.template = self.info["template"]
        if "bias" in self.info and self.info["bias"]:
            self.template += self.info["bias"]
        self.client_kwargs = self.info.get("client_kwargs", {})
        if instruction_type is None:
            if "{instruction}" not in self.template:
                self.instruction = None
                self.partial_filled_template = self.template
            else:
                raise ValueError("'instruction' key is not in template")
        else:
            if instruction_type == "dialogue":
                self.instruction = (
                    dialogue_instruction
                    if dialogue_instruction is not None
                    else self.DEFAULT_DIALOGUE_INSTRUCTION
                )
            elif instruction_type == "direct":
                self.instruction = (
                    direct_instruction
                    if direct_instruction is not None
                    else self.DEFAULT_DIRECT_INSTRUCTION
                )
            else:
                raise ValueError(f"unknown instruction type {instruction_type}")
            self.partial_filled_template = str(
                Template(self.template, ensure_complete=False).format(
                    {"instruction": self.instruction}
                )
            )
        if max_new_tokens is None:
            raise ValueError("provide a value for max_new_tokens other than None")
        self.max_new_tokens = max_new_tokens

    def meta(self):
        return {"prompt": self.partial_filled_template}

    def preprocess(self, text):
        return text

    def postprocess(self, generated):
        return generated

    def __call__(
        self, text, temperature=0, top_p=0.5, frequency_penalty=0, presence_penalty=0
    ):
        text = self.preprocess(text)
        if self.is_chat:
            prompt = (self.instruction, text)
        else:
            prompt = self.template.format(instruction=self.instruction, input=text)
        result = self.client(
            prompt,
            max_new_tokens=self.max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            **self.client_kwargs,
        )
        generated = result["generated"]
        generated = self.postprocess(generated)
        return generated


class ClusterToLabel(TaskBase):
    DEFAULT_DIRECT_INSTRUCTION = "Every input is the content of a debate. For every input, you generate a single descriptive phrase that describes that input in very simple language, without talking about the debate or the author."
    DEFAULT_DIALOGUE_INSTRUCTION = """A chat between a curious user and an artificial intelligence assistant.
The user presents a debate and the assistant generates a single descriptive phrase that describes the debate in very simple language, without talking about the debate or the author."""

    def __init__(self, client, *args, max_length=None, **kwargs):
        super().__init__(client, *args, **kwargs)
        if max_length is None:
            max_length = self.info.pop("max_length", float("inf"))
        self.max_length = min(max_length, client.meta()["model_max_length"])

    def preprocess(self, text):
        text = sorted(text, key=lambda x: x["lambda"], reverse=True)
        text = [e["text"] for e in text]
        if isinstance(self.client, OpenAIClient):
            multiplier = 1
            backoff = 10
        else:
            multiplier = 0.8
            backoff = 0
        text = trim_text(
            client=self.client,
            template=self.partial_filled_template,
            text=text,
            model_max_length=self.max_length,
            max_length=self.max_length * multiplier,
            max_new_tokens=self.max_new_tokens,
            backoff=backoff,
        )
        return text

    def postprocess(self, generated):
        cleaned = clean(generated)
        cleaned = cleaned.strip('"')
        return cleaned


class LabelToMediaFrame(TaskBase):
    DEFAULT_DIRECT_INSTRUCTION = """The following list contains all available media frames as defined in the work from Boydstun, Amber E. et al. "Tracking the Development of Media Frames within and across Policy Issues." (2014): ["economic", "capacity and resources", "morality", "fairness and equality", "legality, constitutionality and jurisprudence", "policy prescription and evaluation", "crime and punishment", "security and defense", "health and safety", "quality of life", "cultural identity", "public opinion", "political", "external regulation and reputation"]
For every input, you answer with three of these media frames corresponding to that input, in order of importance."""

    DEFAULT_DIALOGUE_INSTRUCTION = """A chat between a curious user and an artificial intelligence assistant.
The assistant knows all media frames as defined in the work from Boydstun, Amber E. et al. "Tracking the Development of Media Frames within and across Policy Issues." (2014): ["economic", "capacity and resources", "morality", "fairness and equality", "legality, constitutionality and jurisprudence", "policy prescription and evaluation", "crime and punishment", "security and defense", "health and safety", "quality of life", "cultural identity", "public opinion", "political", "external regulation and reputation"]
The assistant answers with three of these media frames corresponding to the user's text, in order of importance."""

    def postprocess(self, generated):
        return parse_frames(generated)
