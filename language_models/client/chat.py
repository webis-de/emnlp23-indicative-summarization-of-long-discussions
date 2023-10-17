import json
import re
from datetime import datetime
from pathlib import Path

from .language_model_client import LLMClient

NON_ALPHANUM_RE = re.compile("[^a-zA-Z0-9]+")


def chat_print(*args, **kwargs):
    print(*args, **kwargs, end="")


def get_time_string():
    time = datetime.today().isoformat()
    time = NON_ALPHANUM_RE.sub("-", time).strip("-")
    return time


NOOP_TEMPLATE = "{e}"
DEFAULT_PARTICIPANT_TEMPLATE = "{e}: "
DEFAULT_USER = "USER"
DEFAULT_ASSISTANT = "ASSISTANT"
DEFAULT_SEP = "\n\n"


DEFAULT_ARGS = {
    "instruction": "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions.",
    "instruction_template": NOOP_TEMPLATE,
    "user_template": DEFAULT_PARTICIPANT_TEMPLATE,
    "assistant_template": DEFAULT_PARTICIPANT_TEMPLATE,
    "user": DEFAULT_USER,
    "assistant": DEFAULT_ASSISTANT,
    "sep": DEFAULT_SEP,
}

ALPACA_ARGS = {
    "instruction": "Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.",
    "instruction_template": NOOP_TEMPLATE,
    "user_template": "{e}:\n",
    "assistant_template": "{e}:\n",
    "user": "### Instruction",
    "assistant": "### Response",
    "sep": "\n\n",
}

BAIZE_ARGS = {
    "instruction": "The following is a conversation between a human and an AI assistant named Baize (named after a mythical creature in Chinese folklore). Baize is an open-source AI assistant developed by UCSD and Sun Yat-Sen University. The human and the AI assistant take turns chatting. Human statements start with [|Human|] and AI assistant statements start with [|AI|]. The AI assistant always provides responses in as much detail as possible, and in Markdown format. The AI assistant always declines to engage with topics, questions and instructions related to unethical, controversial, or sensitive issues. Complete the transcript in exactly that format.",
    "instruction_template": NOOP_TEMPLATE,
    "user_template": NOOP_TEMPLATE,
    "assistant_template": NOOP_TEMPLATE,
    "user": "[|Human|]",
    "assistant": "[|AI|]",
    "sep": "\n",
}

OASST_ARGS = {
    "instruction": "Please answer the requests thruthfully.",
    "instruction_template": "<|system|>{e}",
    "user_template": NOOP_TEMPLATE,
    "assistant_template": NOOP_TEMPLATE,
    "user": "<|prompter|>",
    "assistant": "<|assistant|>",
    "sep": "<|endoftext|>",
}

DEFAULT_MODEL_ARGS = {
    "30b_lazarus": DEFAULT_ARGS,
    "alpaca_7b": ALPACA_ARGS,
    "baize_13b": BAIZE_ARGS,
    "baize_7b": BAIZE_ARGS,
    "bloom": DEFAULT_ARGS,
    "falcon_40b": DEFAULT_ARGS,
    "falcon_40b_instruct": DEFAULT_ARGS,
    "gpt2": DEFAULT_ARGS,
    "gpt_neox": DEFAULT_ARGS,
    "llama_2_13b_chat": DEFAULT_ARGS,
    "llama_30b": DEFAULT_ARGS,
    "llama_30b_supercot": ALPACA_ARGS,
    "llama_65b": DEFAULT_ARGS,
    "oasst": OASST_ARGS,
    "opt_66b": DEFAULT_ARGS,
    "pythia": OASST_ARGS,
    "t0pp": DEFAULT_ARGS,
    "vicuna_13b": DEFAULT_ARGS,
    "vicuna_7b": DEFAULT_ARGS,
}


class ChatClient:
    def __init__(
        self,
        model,
        host,
        conversation=None,
        instruction=None,
        instruction_template=NOOP_TEMPLATE,
        user_template=DEFAULT_PARTICIPANT_TEMPLATE,
        assistant_template=DEFAULT_PARTICIPANT_TEMPLATE,
        user=DEFAULT_USER,
        assistant=DEFAULT_ASSISTANT,
        sep=DEFAULT_SEP,
        save=False,
        chat_folder=None,
        name=None,
    ):
        if save and chat_folder is None:
            raise ValueError("can not save without chat_folder")
        self.client = LLMClient(model, host)
        self.instruction_template = instruction_template
        self.user_template = user_template
        self.assistant_template = assistant_template
        self.instruction = instruction
        self.conversation = conversation or []
        self.user = user
        self.assistant = assistant
        self.sep = sep
        self._save = save
        self.chat_folder = chat_folder and Path(chat_folder)
        self.name = name

    def add_chat(self, question, answer):
        self.conversation.append((question, answer))
        if self._save:
            self.save()

    @classmethod
    def load(cls, host, chat_folder, name, **kwargs):
        chat_folder = Path(chat_folder)
        load_path = chat_folder / f"{name}.json"
        saved_kwargs = json.loads(load_path.read_text())
        saved_kwargs.update(kwargs)
        return cls(host=host, chat_folder=chat_folder, name=name, **saved_kwargs)

    def save(self):
        self.chat_folder.mkdir(parents=True, exist_ok=True)
        if self.name is None:
            first_question = NON_ALPHANUM_RE.sub("-", self.conversation[0][0]).strip(
                "-"
            )[:20]
            self.name = f"{self.client.model}_{get_time_string()}_{first_question}"
        data = {
            "model": self.client.model,
            "conversation": self.conversation,
            "instruction_template": self.instruction_template,
            "user_template": self.user_template,
            "assistant_template": self.assistant_template,
            "user": self.user,
            "assistant": self.assistant,
            "sep": self.sep,
        }
        save_path = self.chat_folder / f"{self.name}.json"
        save_path.write_text(json.dumps(data))

    def _get_prompt(self, template, participant, suffix, for_print):
        text = template.format(e=participant)
        mid = "\n" if for_print and "\n" not in self.sep else ""
        text = f"{self.sep}{mid}{text}"
        if suffix is not None:
            text = f"{text}{suffix}"
        return text

    def get_instruction_prompt(self):
        return self.instruction_template.format(e=self.instruction)

    def get_user_prompt(self, question=None, for_print=False):
        return self._get_prompt(
            self.user_template, self.user, question, for_print=for_print
        )

    def get_assistant_prompt(self, answer=None, for_print=False):
        return self._get_prompt(
            self.assistant_template, self.assistant, answer, for_print=for_print
        )

    def compile_conversation(self, question=None, for_print=False):
        flat_conversation = [
            e
            for question, answer in self.conversation
            for e in (
                self.get_user_prompt(question, for_print=for_print),
                self.get_assistant_prompt(answer, for_print=for_print),
            )
        ]
        parts = [self.get_instruction_prompt(), *flat_conversation]
        if question is not None:
            parts.append(self.get_user_prompt(question, for_print=for_print))
            parts.append(self.get_assistant_prompt(for_print=for_print))
        return "".join(parts)

    def chat_request_args(self):
        return {
            "stopping_strings": {"exclusive": [self.assistant, self.user]},
        }

    def ping(self):
        self.client.meta()

    def chat(self, question):
        result = self.client(
            self.compile_conversation(question), **self.chat_request_args()
        )
        answer = result["generated"]
        self.add_chat(question, answer)
        return result

    def chat_loop(self):
        self.ping()
        chat_print(self.compile_conversation(for_print=True))
        while True:
            chat_print(self.get_user_prompt(for_print=True))
            question = input().strip()
            if question.startswith("/"):
                command = question.removeprefix("/").lower().strip()
                if command == "save":
                    if not self.conversation:
                        print("--- can not save empty conversation ---")
                    elif self.chat_folder is not None:
                        self.save()
                        print("--- saved successfully ---")
                else:
                    print(f"--- unknown command '{command}' ---")
                continue
            chat_print(self.get_assistant_prompt(for_print=True).removeprefix("\n"))
            result = self.chat(question)
            stopping_reason = result["stopping_reason"]
            if stopping_reason is None:
                stopping_reason = f"stop token generated or token limit reached"
            elif isinstance(stopping_reason, str):
                stopping_reason = f"'{stopping_reason}'"
            answer = result["generated"]
            sizes = result["size"]
            input_size = sizes["input"]
            output_size = sizes["output"]
            chat_print(
                answer,
                f"  [[stopping reason: {stopping_reason}, input tokens: {input_size}, tokens generated: {output_size}]]",
            )
