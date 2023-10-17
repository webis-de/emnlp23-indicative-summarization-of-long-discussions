#!/usr/bin/env python3

import json
from collections import OrderedDict, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).parent.parent / "data"
EXAMPLES_PATH = DATA_PATH / "examples.json"
USER_PATH = DATA_PATH / "users"
REPORT_PATH = DATA_PATH / "pilot_result.html"

examples = json.loads(EXAMPLES_PATH.read_text())
examples = sorted(examples.items(), key=lambda x: x[0])
examples = OrderedDict(examples[:20])

results = defaultdict(dict)
user_paths = list(USER_PATH.glob("*-*.json"))
assert len(user_paths) == 4
for path in user_paths:
    user = path.name
    user = user[: user.find("-")]
    user_data = json.loads(path.read_text())
    for example_id, value in examples.items():
        num_examples = len(value["hypotheses"])
        ranking = user_data[example_id]
        results[example_id][user] = ranking

COLORS = [
    "#bbffff",
    "#ffddff",
    "#ffffcc",
    "#ddddff",
    "#ffdddd",
    "#ddffdd",
]

rng = np.random.default_rng()


def row_to_html(row):
    table_row = ["<tr>"]
    table_row.extend(
        [
            f'<td style="background-color: {bgcolor};">{text}</td>'
            for text, bgcolor in row
        ]
    )
    table_row.append("</tr>")
    table_row = "\n".join(table_row)
    return table_row


def columns_to_html(columns):
    table_head = ["<tr>"]
    table_head.extend([f"<th>{column}</th>" for column in columns])
    table_head.append("</tr>")
    table_head = "\n".join(table_head)
    return table_head


def df_to_html(df):
    table = ["<table>"]
    table.append("<thead>")
    table.append(columns_to_html(df.columns))
    table.append("</thead>")
    table.append("<tbody>")
    table.extend([row_to_html(row) for _, row in df.iterrows()])
    table.append("</tbody>")
    table.append("</table>")
    table = "\n".join(table)
    return table


entries = []
for i, (key, value) in enumerate(results.items(), start=1):
    reference = examples[key]["reference"]
    hypotheses = examples[key]["hypotheses"]
    df = pd.DataFrame(value)
    random_order = list(set(df.values.ravel()))
    rng.shuffle(random_order)
    random_map = {key: COLORS[i] for i, key in enumerate(random_order)}
    df = df.applymap(lambda x: (hypotheses[x], random_map[x]))
    table = df_to_html(df)
    entry = f"<h3>{i} {reference}</h3>\n{table}"
    entries.append(entry)

entries = "\n<hr /> \n".join(entries)

html = f"""
<html>
<head>
<title>pilot study</title>
</head>
<body>
{entries}
</body>
</html>
"""

REPORT_PATH.write_text(html)
