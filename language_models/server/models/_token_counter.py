import numpy as np

from ._stream_detokenizer import StreamDetokenizer


class TokenCounter:
    def __init__(self, tokenizer, texts, indicate_shared=False):
        self.is_single = isinstance(texts, str)
        if self.is_single:
            texts = [texts]
        tokenized = tokenizer(
            ["".join(texts)],
            truncation=False,
            return_token_type_ids=False,
            return_attention_mask=False,
            return_special_tokens_mask=True,
            return_offsets_mapping=tokenizer.is_fast,
            return_length=True,
        )
        (special_tokens_mask,) = tokenized["special_tokens_mask"]
        if tokenizer.is_fast:
            (offsets_mapping,) = tokenized["offset_mapping"]
            self.ends = [
                end
                for (_, end), special in zip(offsets_mapping, special_tokens_mask)
                if special == 0
            ]
        else:
            (input_ids,) = tokenized["input_ids"]
            detokenizer = StreamDetokenizer(tokenizer)
            self.ends = np.cumsum(
                [
                    len(detokenizer(token))
                    for token, special in zip(input_ids, special_tokens_mask)
                    if special == 0
                ]
            )
        (self.num_all_tokens,) = tokenized["length"]
        self.num_non_special_tokens = len(self.ends)
        self.num_special_tokens = self.num_all_tokens - self.num_non_special_tokens
        self.counts = []
        self.current_count = 0
        self.current_length = 0
        self.length_iter = iter(np.cumsum([len(e) for e in texts]))
        self.indicate_shared = indicate_shared

    def results(self):
        return {
            "counts": self.counts,
            "num": {
                "all": self.num_all_tokens,
                "special": self.num_special_tokens,
                "non_special": self.num_non_special_tokens,
            },
        }

    def _commit_count(self, is_partial):
        if self.indicate_shared and is_partial:
            self.current_count += 0.5
        self.counts.append(self.current_count)
        self.current_count = 0

    def _get_next_length(self, is_partial):
        while (next_length := next(self.length_iter)) == self.current_length:
            self._commit_count(is_partial)
        return next_length

    def consume(self):
        if self.counts:
            raise Exception("already consumed")
        try:
            self.current_length = self._get_next_length(False)
            for end in self.ends:
                self.current_count += 1
                while self.current_length <= end:
                    self._commit_count(self.current_length != end)
                    self.current_length = self._get_next_length(
                        self.current_length != end
                    )
        except StopIteration:
            pass
        if self.is_single:
            (self.counts,) = self.counts
        return self.counts
