import re
from datetime import datetime

import pandas as pd

from ....logger import LOGGER
from .util import yml_load_entries


def _format_ymd(year: str | int, month: str | int, day: str | int) -> str | None:
    try:
        y = int(year)
        if y < 100:
            y += 2000
        m = int(month)
        d = int(day)
        return f"{y:04d}-{m:02d}-{d:02d}"
    except Exception:
        return None


def _get_date_from_title(title: str, regexp: re.Pattern) -> str | None:
    """Extract YYYY-MM-DD from title.

    Supports regexes with named groups 'year','month','day' or positional groups.
    For 3 positional groups it heuristically detects whether the year is first
    (YYYY/MM/DD) or last (MM/DD/YYYY or MM/DD/YY).
    Returns None for 2-group matches (month/day) — use the upload-date variant then.
    """
    match = regexp.search(title)
    if not match:
        return None

    gd = match.groupdict()
    if gd:
        y = gd.get("year") or gd.get("y")
        m = gd.get("month") or gd.get("m")
        d = gd.get("day") or gd.get("d")
        if y and m and d:
            return _format_ymd(y, m, d)
        return None

    groups = match.groups()
    if len(groups) == 3:
        g0, g1, g2 = groups
        # if first group looks like YYYY, assume Y-M-D
        if re.fullmatch(r"\d{4}", str(g0)):
            return _format_ymd(g0, g1, g2)
        # otherwise assume last group is year (possibly two-digit)
        return _format_ymd(g2, g0, g1)
    # len == 2 (MM/DD) => cannot determine year here
    return None


def _get_date_from_title_and_upload_date(
    title: str, upload_date: str, regexp: re.Pattern
) -> str | None:
    """Extract YYYY-MM-DD from title using upload_date as fallback year.

    Prefer named groups ('month','day'). Fall back to first two positional groups.
    """
    match = regexp.search(title)
    if not match:
        return None

    gd = match.groupdict()
    if gd:
        month = gd.get("month") or gd.get("m")
        day = gd.get("day") or gd.get("d")
    else:
        groups = match.groups()
        if len(groups) < 2:
            return None
        month, day = groups[0], groups[1]

    try:
        upload_dt = datetime.strptime(upload_date, "%Y%m%d")
        year = upload_dt.year
    except Exception:
        return None

    return _format_ymd(year, month, day)  # type: ignore


def _process_general_entries(
    key: str,
    regexp: re.Pattern,
    add_year: bool = False,
    filter_str: str | None = None,
) -> dict[str, str]:
    data = yml_load_entries(key)
    if len(data) == 0:
        return {}

    if add_year:
        dates = [
            _get_date_from_title_and_upload_date(
                record["title"], record["upload_date"], regexp
            )
            for record in data
        ]
    else:
        dates = [_get_date_from_title(record["title"], regexp) for record in data]
    ids = [record["id"] for record in data]
    titles = [record["title"] for record in data]
    df = pd.DataFrame({"date": dates, "id": ids, "title": titles})
    if filter_str:
        df = df[df["title"].str.lower().str.contains(filter_str)]
    nan_mask = df["date"].isna()
    df = df[~nan_mask]
    if (num_nan := nan_mask.sum()) > 0:
        LOGGER.info(f"{key}: Removed {num_nan} unparsable entries.")
    num_dup = df["date"].duplicated().sum()
    if num_dup > 0:
        LOGGER.info(
            f"{key}: Found {num_dup} duplicate dates, keeping first occurrence."
        )
    df = df.sort_values("date").drop_duplicates("date", keep="first")
    date_to_id = dict(zip(df["date"], df["id"]))
    return date_to_id


PROCESSOR_DICT = {
    "jnails_dailies": lambda: _process_general_entries(
        "jnails_dailies",
        re.compile(r"(?P<month>\d{1,2})/(?P<day>\d{1,2})"),
        True,
    ),
    "rdon_dailies": lambda: _process_general_entries(
        "rdon_dailies",
        re.compile(r"(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})"),
    ),
    "mic_dailies": lambda: _process_general_entries(
        "mic_dailies",
        re.compile(r"(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{2})"),
    ),
    "holz_dailies": lambda: _process_general_entries(
        "holz_dailies",
        re.compile(r"(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})"),
        False,
        "daily dominion",
    ),
    "yudai_dailies": lambda: _process_general_entries(
        "yudai_dailies",
        re.compile(r"(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})"),
        False,
        "tgg daily dominion",
    ),
    "sharur_dailies": lambda: _process_general_entries(
        "sharur_dailies",
        re.compile(r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"),
    ),
    "fabyy_dailies": lambda: _process_general_entries(
        "fabyy_dailies",
        re.compile(r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"),
    ),
}
