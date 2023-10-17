from transformers import StoppingCriteria, StoppingCriteriaList

from ._stream_detokenizer import StreamDetokenizer


class StringStoppingCriteria(StoppingCriteria):
    def __init__(
        self,
        tokenizer,
        *,
        prompt=None,
        inclusive=None,
        exclusive=None,
    ):
        super().__init__()
        self.stream_detokenizer = StreamDetokenizer(tokenizer)
        self.inclusive = self.convert_stopping_definitions(prompt, inclusive)
        self.exclusive = self.convert_stopping_definitions(prompt, exclusive)
        self.is_empty = len(self.inclusive) + len(self.exclusive) == 0
        self.decoded = ""
        self.stop_string = None

    @staticmethod
    def convert_stopping_definitions(prompt, stopping_definitions):
        if prompt is None or not isinstance(stopping_definitions, dict):
            if not stopping_definitions:
                return []
            return stopping_definitions
        stripped = prompt.rstrip()
        stopping_strings = set()
        if None in stopping_definitions:
            stopping_strings.update(stopping_definitions.pop(None))
        valid_definitions = {
            k: v for k, v in stopping_definitions.items() if stripped.endswith(k)
        }
        if valid_definitions:
            max_length = max(len(e) for e in valid_definitions.keys())
            for key_character, stop_chars in stopping_definitions.items():
                if len(key_character) == max_length:
                    stopping_strings.update(stop_chars)
        return stopping_strings

    def _contains_stop_string(self, stop_set, token, remove):
        for string in stop_set:
            lookback = len(string) + len(token) - 1
            if string in self.decoded[-lookback:]:
                self.stop_string = string
                self.remove = remove
                return True

    def should_stop(self, token):
        if self.is_empty:
            return False
        if not isinstance(token, str):
            token = self.stream_detokenizer(token)
        self.decoded += token
        return self._contains_stop_string(
            self.exclusive, token, True
        ) or self._contains_stop_string(self.inclusive, token, False)

    def __call__(self, input_ids, _):
        try:
            input_id = input_ids[0, -1].item()
        except IndexError:
            return False
        return self.should_stop(input_id)

    def trim(self, generated):
        if self.stop_string is not None:
            offset = len(self.stop_string) if not self.remove else 0
            generated = generated[: generated.rfind(self.stop_string) + offset].rstrip()
        return generated

    def tolist(self):
        if self.is_empty:
            return None
        return StoppingCriteriaList([self])


def merge_set_dicts(dict1, dict2):
    if not dict1:
        return dict2
    if not dict2:
        return dict2
    new_dict = {}
    keys = set(dict1.keys()) | set(dict2.keys())
    for key in keys:
        new_dict[key] = set(dict1.get(key, {})) | set(dict2.get(key, {}))
    return new_dict


def merge_stopping_criterias(inclusive, exclusive, stopping_strings):
    if stopping_strings:
        inclusive = merge_set_dicts(
            inclusive, {None: stopping_strings.get("inclusive", [])}
        )
        exclusive = merge_set_dicts(
            exclusive, {None: stopping_strings.get("exclusive", [])}
        )
    return inclusive, exclusive
