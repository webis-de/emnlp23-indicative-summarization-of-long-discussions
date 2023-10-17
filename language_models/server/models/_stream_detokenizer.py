class StreamDetokenizer:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.prev_tokens = []

    def _decode(self, tokens):
        return self.tokenizer.decode(tokens, skip_special_tokens=False)

    def __call__(self, token):
        prefix_text = self._decode(self.prev_tokens)
        self.prev_tokens.append(token)
        new_text = self._decode(self.prev_tokens)
        new_text = "" if new_text.endswith("�") else new_text[len(prefix_text) :]
        if new_text:
            self.prev_tokens = [token]
        return new_text
