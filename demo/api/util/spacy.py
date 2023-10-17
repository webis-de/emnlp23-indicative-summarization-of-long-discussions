import re

import spacy

SPACE_RE = re.compile(r"\s+")


class Spacy:
    MODEL = "en_core_web_md"
    _instance = None

    def __init__(self):
        self.nlp = spacy.load(self.MODEL)

    def split_sentences(self, text):
        return [sent.text for sent in self.nlp(SPACE_RE.sub(" ", text).strip()).sents]

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def setup(cls, user=False):
        if not spacy.util.is_package(cls.MODEL):
            pip_args = []
            if user:
                pip_args.append("--user")
            print(f"downloading {cls.MODEL}")
            spacy.cli.download(cls.MODEL, False, False, *pip_args)
