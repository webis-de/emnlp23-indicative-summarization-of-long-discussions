import re

pre = "(complex|complicated|nuanced|heated|passionate)"
over = "(over|about|between|centers|explores|discusses|focuses|on)"
over_post = "(of|about|on|against|for|around|is)"
after = f"({over} )?({over_post} )?(the (concept of )?)?"
verbs = "(explor|believ|suggest|struggl|propos|argu|discuss|debat|examin|explor)(ing|e|es|s)"

PREAMBLE_RE = re.compile(
    "^(- )?(descriptive phrase|debate topic|input( [0-9]+)?) *: *",
    flags=re.IGNORECASE,
)

DEBATE_RE = re.compile(
    rf"^((A|the) )?({pre} (and {pre} )?)?((considerations|dispute|debate|argument|discussion)s? )(is )?{after} *",
    flags=re.IGNORECASE,
)

DEBATING_RE = re.compile(
    rf"^(([a-zA-Z0-9]+ ){{,3}}(person|people|professional|user) )?((is|are) )?({verbs} ){after}(that )? *",
    flags=re.IGNORECASE,
)

NON_ALPHANUM_RE = re.compile("[a-zA-Z0-9]")

AFTER_RE = re.compile(
    rf"(, ((with|but) (.*arguments|(some|one) .*{verbs})|including arguments).*|are discussed.?|argument.?)$",
    flags=re.IGNORECASE,
)

SENTENCE_RE = re.compile(r"(.*?(?:[.!?] |$))")

WORD_RE = re.compile("[a-zA-Z0-9-_']+")

ERROR_INDICATORS = [
    "debate or the author",
    "curious user",
    "ai assistant",
    "artificial intelligence assistant",
    "descriptive phrase",
]


def is_erroneous(text):
    lower_text = text.lower()
    return any(e in lower_text for e in ERROR_INDICATORS)


def find_first_sentence(text):
    matches = SENTENCE_RE.findall(text)
    sentences = []
    curr_sentence = ""
    for match in matches:
        match = match.strip()
        curr_sentence += f" {match}"
        match_lower = match.lower()
        words = match_lower.split()
        last_word = words[-1] if words else ""
        words_without_dot = match_lower.replace(".", "").split()
        last_word_without_dot = words_without_dot[-1] if words_without_dot else ""
        if not match_lower.endswith(".") or (
            sum("." == e for e in last_word) <= 1
            and last_word_without_dot not in ["us", "vs", "etc", "eg"]
        ):
            sentences.append(curr_sentence.strip())
            curr_sentence = ""
    return sentences[0]


def count_words(text):
    words = WORD_RE.findall(text)
    return len(words)


def clean(text):
    lines = text.splitlines()
    text = max(
        [[len(NON_ALPHANUM_RE.sub("", line)), line] for line in lines],
        key=lambda x: x[0],
    )[1]
    text = PREAMBLE_RE.sub("", text)
    text = DEBATE_RE.sub("", text)
    text = DEBATING_RE.sub("", text)
    text = AFTER_RE.sub("", text)
    text = text.strip()
    if count_words(text) > 15:
        text = find_first_sentence(text)
    text = text.strip()
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    return text
