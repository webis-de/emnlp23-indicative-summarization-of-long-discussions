import re

# examples = ["A complex debate on the ", "A complex debate about the ", "A complex discussion about the ", "A complex discussion about", "A complex discussion of the", "A debate about the ", "A debate over the ", "A discussion about ", "A discussion about the", "A discussion of the", "A complex and nuanced discussion about the ", "The argument about the ", "A discussion on ", "A discussion on the", "A heated discussion about the ", "A heated discussion on the", "Two people arguing about the ", "A passionate discussion about the", "Argument about", "Complex discussion of the", "Complex discussion", "Complicated discussion of", "Debate about ", "Debate about ", "Debate about the", "Debating the ", "Discussing the ", "Discussing the ", "Discussion about ", "Discussion about the ", "Discussion on ", "Discussion on the", "Discussions about the ", "Dispute over ", "Examining ", "Examining the ", "Exploring the", "The debate about the ", "The debate between ", "The debate between the ", "The debate centers on the ", "The debate explores the ", "The debate centers around the ", "The debate discusses the ", "The debate discusses the ", "The debate focuses on the ", "The debate explores the ", "The debate is about the ", "The debate explores the concept of ", "The debate on the ", "The debate over ", "The debate over the ", "The user discusses the ", "considerations about the ", "discussing"]

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


ERROR_INDICATORS = [
    "debate or the author",
    "curious user",
    "ai assistant",
    "artificial intelligence assistant",
    "descriptive phrase",
]


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


WORD_RE = re.compile("[a-zA-Z0-9-_']+")


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
