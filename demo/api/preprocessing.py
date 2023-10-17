import re
import unicodedata

from bs4 import BeautifulSoup
from unidecode import unidecode
from util.spacy import Spacy

empty_re = re.compile("^[^a-zA-Z]*$")
normalize_re = re.compile(r"\s+")
replace_re = re.compile("[^a-zA-Z0-9'\"()[]-.!$%&:?`*,+;{}]")
noise = [
    "Hello, users of CMV! This is a footnote from your moderators",
    "[deleted]",
    "[removed]",
    "[Wiki][Code][/r/DeltaBot]",
    "[History]",
    "your comment has been removed:",
    "If you would like to appeal, please message the moderators by clicking this link.",
    "This comment has been overwritten by an open source script to protect",
    "Then simply click on your username on Reddit, go to the comments tab, scroll down as far as possibe (hint:use RES), and hit the new OVERWRITE button at the top.",
]

SPECIAL_CONTROL_SEQUENCES = {"\n", "\t"}


def clean_text(text):
    text = unidecode(text)
    text = "".join(
        [
            letter
            for letter in text
            if unicodedata.category(letter) != "Cc"
            or letter in SPECIAL_CONTROL_SEQUENCES
        ]
    )
    return text.strip()


def clean_child(child):
    if child.name in ["ol", "ul"]:
        return [t for c in child.children for t in clean_child(c)]
    if child.name in ["blockquote"]:
        return []
    text = child.text
    for n in noise:
        if n in text:
            return []
    text = clean_text(text)
    if empty_re.match(text):
        return []
    text = replace_re.sub(" ", text)
    text = normalize_re.sub(" ", text).strip()
    return [text]


def segment_text(text):
    if not text:
        return []
    if empty_re.match(text):
        return []
    soup = BeautifulSoup(text, "lxml")
    children = list(soup.div.children)

    valid_text = []
    for child in children:
        valid_text.extend(clean_child(child))
    valid_text = [
        sent
        for section in valid_text
        for sent in Spacy.instance().split_sentences(section)
    ]
    return valid_text
