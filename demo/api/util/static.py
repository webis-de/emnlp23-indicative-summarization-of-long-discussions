import json
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parent.parent
STATIC_PATH = ROOT_PATH / "static.json"
EVALUATION_PATH = ROOT_PATH / "evaluation_discussions.json"

SOURCES = [
    "https://www.reddit.com/r/changemyview/comments/11bqmmi/cmv_the_others_have_it_worse_argument_is_terrible/",
    "https://www.reddit.com/r/changemyview/comments/11dqb6y/cmv_corporations_support_the_lgbt_for_money_not/",
    "https://www.reddit.com/r/changemyview/comments/udzffi/cmv_adults_should_be_able_to_order_from_the_kids/",
    "https://www.reddit.com/r/changemyview/comments/ugsunn/cmv_cosmetic_procedures_on_dogs_like_tail_docking/",
    "https://www.reddit.com/r/changemyview/comments/uxwp0y/cmv_today_is_the_best_time_period_in_human/",
    "https://www.reddit.com/r/changemyview/comments/wqwiiz/cmv_there_shouldnt_be_anything_other_than_the/",
    "https://www.reddit.com/r/changemyview/comments/xdgmvg/cmv_religion_holds_humanity_back/",
    "https://www.reddit.com/r/changemyview/comments/xs35tq/cmv_shoe_sizes_should_be_the_same_for_both_men/",
    "https://www.reddit.com/r/changemyview/comments/ynqtgx/cmv_social_media_is_the_most_destructive/",
    "https://www.reddit.com/r/changemyview/comments/zob4xe/cmv_the_words_master_and_slave_should_not_be/",
    "https://www.reddit.com/r/changemyview/comments/zvque9/cmv_everything_happens_for_a_reason_is_such_an/",
]


def load_static():
    try:
        return json.loads(STATIC_PATH.read_text())
    except FileNotFoundError:
        return {}


def write_static(static):
    STATIC_PATH.write_text(json.dumps(static))


def load_evaluation_discussions():
    try:
        return json.loads(EVALUATION_PATH.read_text())
    except FileNotFoundError:
        return {}
