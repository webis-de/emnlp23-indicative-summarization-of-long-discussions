from typing import Dict, List, Literal, Optional, Set, Union

import torch
from petals import DistributedBloomForCausalLM
from pydantic import BaseModel, Field
from transformers import BloomTokenizerFast

from ._stopping_criteria import (StringStoppingCriteria,
                                 merge_stopping_criterias)
from ._token_counter import TokenCounter

MODEL_NAME = "bigscience/bloom-petals"

INCLUSIVE_STOPPING_STRINGS = {'"': ['"'], '["': ["]"]}
EXCLUSIVE_STOPPING_STRINGS = {None: ["</s>"]}


class TokenizeModel(BaseModel):
    text: Union[List[str], str]
    indicate_shared: bool = False


class Model:
    TYPE = "generation"
    MAX_LENGTH = 2048
    MAX_NEW_TOKENS = 64

    def __init__(self):
        self.tokenizer = BloomTokenizerFast.from_pretrained(
            MODEL_NAME, model_max_length=self.MAX_LENGTH
        )
        self.model = DistributedBloomForCausalLM.from_pretrained(
            MODEL_NAME, request_timeout=300
        ).cuda()

    def get_meta(self):
        return {
            "model_max_length": self.tokenizer.model_max_length,
        }

    def router_hook(self, router):
        def tokenizer_count(body: TokenizeModel):
            counter = TokenCounter(self.tokenizer, body.text, body.indicate_shared)
            counter.consume()
            return counter.results()

        router.post("/tokenizer/count")(tokenizer_count)

    def get_string_stopping_criteria(self, prompt, stopping_strings):
        inclusive, exclusive = merge_stopping_criterias(
            INCLUSIVE_STOPPING_STRINGS, EXCLUSIVE_STOPPING_STRINGS, stopping_strings
        )
        return StringStoppingCriteria(
            self.tokenizer,
            prompt=prompt,
            inclusive=inclusive,
            exclusive=exclusive,
        )

    def inference(self, prompt, max_new_tokens, stopping_strings=None):
        with torch.inference_mode():
            output = []
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").cuda()
            num_input_tokens = len(inputs[0])
            stopping_criteria = self.get_string_stopping_criteria(
                prompt, stopping_strings
            )
            with self.model.inference_session(
                max_length=num_input_tokens + max_new_tokens
            ) as session:
                while len(output) < max_new_tokens:
                    (current_output,) = self.model.generate(
                        inputs, max_new_tokens=1, do_sample=False, session=session
                    )
                    inputs = None
                    new_token_id = current_output[-1].item()
                    output.append(new_token_id)
                    new_token = self.tokenizer.decode(new_token_id)
                    print(new_token, end="", flush=True)
                    if stopping_criteria.should_stop(new_token):
                        break
                print(flush=True)
                num_output_tokens = len(output)
                num_overflow_tokens = 0
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
            MAX_NEW_TOKENS,
            description="the number of tokens that the model will generate at most",
            gt=0,
        ),
        stopping_strings: Optional[
            Dict[Literal["inclusive", "exclusive"], Set[str]]
        ] = Field(
            None,
            description="The strings to stop on, inclusive will return stopping string while exclusive will not.",
        ),
    ):
        return [
            self.inference(
                prompt, max_new_tokens=max_new_tokens, stopping_strings=stopping_strings
            )
            for prompt in batch
        ]
