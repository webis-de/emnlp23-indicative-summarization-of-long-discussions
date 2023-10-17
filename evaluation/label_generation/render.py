import numpy as np
import pandas as pd


def get_diff_indexes(arr, add_end=False):
    if len(arr) == 0:
        return []
    counter = 0
    all_keys = {}
    new_arr = []
    for e in arr:
        if e not in all_keys:
            all_keys[e] = counter
            counter += 1
        new_arr.append(all_keys[e])
    if add_end:
        new_arr.append(counter)
    diff_arr = np.diff(new_arr)
    (indices,) = np.where(diff_arr != 0)
    indices += 1
    indices = [0, *(int(e) for e in indices)]
    return indices


def ltext(text, bold=True, ttfamily=False):
    if not text:
        return text
    text = text.replace("_", r"\_")
    if ttfamily:
        text = rf"\ttfamily{{{text}}}"
    if bold:
        text = rf"\textbf{{{text}}}"
    return text


def to_latex(df, precision):
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.map(lambda x: tuple(ltext(e) for e in x))
        first = df.columns.get_level_values(0)
        diffs = get_diff_indexes(first, add_end=True)
        spans = []
        for start, end in zip(diffs, diffs[1:]):
            start = start + 1
            if start != end:
                spans.append(rf"\cmidrule(lr){{{start}-{end}}}")
        extra = "".join(spans)
    else:
        df.columns = df.columns.map(lambda x: ltext(x))
        extra = None
    df.iloc[:, 0] = df.iloc[:, 0].map(lambda x: ltext(x, ttfamily=False))
    text = df.to_latex(
        index=False,
        float_format=f"%.{precision}f",
        bold_rows=True,
        na_rep="--",
        multicolumn_format="c",
    ).strip()
    if extra:
        lines = text.splitlines()
        lines.insert(3, extra)
        text = "\n".join(lines)
    return f"```latex\n{text}\n```"


STYLES = {
    "markdown": lambda x, _: x.to_markdown(index=False),
    "latex": to_latex,
    "csv": lambda x, precision: x.to_csv(index=False, float_format=f"%.{precision}f"),
}
