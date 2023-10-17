import enum
import gc
from pathlib import Path
from typing import Dict, List, Literal, Optional, Set, Union

import numpy as np
import torch
from pydantic import BaseModel, Field
from transformers import (AutoModelForCausalLM, AutoModelForSeq2SeqLM,
                          AutoTokenizer)

from ._stopping_criteria import (StringStoppingCriteria,
                                 merge_stopping_criterias)
from ._token_counter import TokenCounter


class TokenizeModel(BaseModel):
    text: Union[List[str], str]
    indicate_shared: bool = False


class ModelTypes(enum.Enum):
    DECODER = enum.auto()
    ENCODER_DECODER = enum.auto()


def get_diff_indexes(arr):
    if len(arr) == 0:
        return []
    diff_arr = np.diff(arr)
    (indices,) = np.where(diff_arr != 0)
    indices += 1
    indices = [0, *(int(e) for e in indices)]
    return indices


def cleanup_cuda(func):
    def wrapper(self, *args, **kwargs):
        if self.is_cuda:
            gc.collect()
            torch.cuda.empty_cache()
        try:
            return func(self, *args, **kwargs)
        finally:
            if self.is_cuda:
                gc.collect()
                torch.cuda.empty_cache()

    return wrapper


def build_transformers_model(
    pretrained_model_name_or_path,
    *,
    model_type=ModelTypes.DECODER,
    setup_path=None,
    default_max_new_tokens=256,
    dtype=torch.float16,
    device_map="balanced",
    inclusive_stopping_strings=None,
    exclusive_stopping_strings=None,
    ommit_prompt=True,
    trust_remote_code=False,
    set_pad_token=False,  # set to True to suppress "Setting `pad_token_id` to `eos_token_id`:2 for open-end generation." warning
    tokenizer_kwargs={},
):
    class Model:
        TYPE = "generation"

        def __init__(self):
            if (
                setup_path is not None
                and not Path(pretrained_model_name_or_path).exists()
            ):
                raise ValueError(
                    f"{pretrained_model_name_or_path} does not exist (did you run {setup_path})"
                )
            self.tokenizer = AutoTokenizer.from_pretrained(
                pretrained_model_name_or_path, **tokenizer_kwargs
            )
            if model_type == ModelTypes.DECODER:
                auto_model_class = AutoModelForCausalLM
            elif model_type == ModelTypes.ENCODER_DECODER:
                auto_model_class = AutoModelForSeq2SeqLM
            else:
                raise ValueError(f"unknown model_type {model_type}")
            self.model = auto_model_class.from_pretrained(
                pretrained_model_name_or_path,
                trust_remote_code=trust_remote_code,
                device_map=device_map,
                torch_dtype=dtype,
            )
            self.is_cuda = str(self.model.device) != "cpu"

        def get_meta(self):
            return {
                "architecture_type": model_type.name.lower(),
                "model_max_length": int(self.tokenizer.model_max_length),
            }

        def router_hook(self, router):
            def tokenizer_count(body: TokenizeModel):
                counter = TokenCounter(self.tokenizer, body.text, body.indicate_shared)
                counter.consume()
                return counter.results()

            router.post("/tokenizer/count")(tokenizer_count)

        def get_string_stopping_criteria(self, prompt, stopping_strings):
            inclusive, exclusive = merge_stopping_criterias(
                inclusive_stopping_strings, exclusive_stopping_strings, stopping_strings
            )
            return StringStoppingCriteria(
                self.tokenizer,
                prompt=prompt,
                inclusive=inclusive,
                exclusive=exclusive,
            )

        def tokenize(self, prompt):
            inputs = self.tokenizer(
                [prompt],
                return_token_type_ids=False,
                truncation=True,
                return_overflowing_tokens=True,
            )
            if self.tokenizer.is_fast:
                non_overflowing_start = get_diff_indexes(
                    inputs["overflow_to_sample_mapping"]
                )
                num_overflow_tokens = [
                    sum(
                        (np.array(e.special_tokens_mask) == 0).sum()
                        for e in inputs.encodings[i].overflowing
                    )
                    for i in non_overflowing_start
                ]
                input_ids = [inputs["input_ids"][i] for i in non_overflowing_start]
                attention_mask = [
                    inputs["attention_mask"][i] for i in non_overflowing_start
                ]
            else:
                num_overflow_tokens = [
                    max(e, 0) for e in inputs["num_truncated_tokens"]
                ]
                input_ids = inputs["input_ids"]
                attention_mask = inputs["attention_mask"]
            return {
                "input_ids": torch.tensor(input_ids),
                "attention_mask": torch.tensor(attention_mask),
            }, num_overflow_tokens

        @cleanup_cuda
        def inference(
            self, prompt, max_new_tokens=default_max_new_tokens, stopping_strings=None
        ):
            with torch.inference_mode():
                inputs, num_overflow_tokens = self.tokenize(prompt)
                num_overflow_tokens = int(num_overflow_tokens[0])
                stopping_criteria = self.get_string_stopping_criteria(
                    prompt, stopping_strings
                )
                num_input_tokens = int(inputs["input_ids"].size()[1])
                if self.is_cuda:
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                generate_args = {
                    "do_sample": False,
                    "stopping_criteria": stopping_criteria.tolist(),
                    "max_new_tokens": max_new_tokens,
                }
                if set_pad_token:
                    generate_args["pad_token_id"] = self.tokenizer.eos_token_id
                (output,) = self.model.generate(**inputs, **generate_args)
                if model_type == ModelTypes.DECODER and ommit_prompt:
                    output = output[num_input_tokens:]
                num_output_tokens = len(output)
                generated = self.tokenizer.decode(output, skip_special_tokens=True)
                generated = stopping_criteria.trim(generated)
                return {
                    "generated": generated,
                    "size": {
                        "input": num_input_tokens,
                        "output": num_output_tokens,
                        "overflow": num_overflow_tokens,
                    },
                    "stopping_reason": stopping_criteria.stop_string,
                }

        def __call__(
            self,
            batch,
            max_new_tokens: int = Field(
                default_max_new_tokens,
                description="The number of tokens that the model will generate at most.",
                gt=0,
            ),
            stopping_strings: Optional[
                Dict[Literal["inclusive", "exclusive"], Set[str]]
            ] = Field(
                None,
                description="The strings to stop on, inclusive will return stopping string while exclusive will not.",
                example={"inclusive": {"."}, "exclusive": {"</s>"}},
            ),
        ):
            return [
                self.inference(
                    prompt,
                    max_new_tokens=max_new_tokens,
                    stopping_strings=stopping_strings,
                )
                for prompt in batch
            ]

    return Model
