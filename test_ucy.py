"""Tests for UCY calendar converter"""

import pytest
from ucy import to_parts, to_ucy, DATUM_TT, ts


TEST_CASES = {
    "Datum -1 day": (ts.tt_jd(DATUM_TT - 1), -1, 45, 7, 0),
    "Datum -1 second": (ts.tt_jd(DATUM_TT - 1 / 86400), -1, 45, 7, 86399000005424),
    "Datum Exact": (ts.tt_jd(DATUM_TT), 0, 0, 0, 0),
    "Datum +1 day": (ts.tt_jd(DATUM_TT + 1), 0, 0, 1, 0),
    "Unix Epoch": (ts.utc(1970, 1, 1), 2012, 36, 1, 53753849896788),
    "Y2K": (ts.utc(2000, 1, 1), 2042, 35, 6, 53775849898159),
    "2025 New Year": (ts.utc(2025, 1, 1), 2067, 36, 2, 53780849911272),
    "Birth of Christ": (ts.utc(1, 12, 25), 44, 35, 5, 53753849896788),
    "Moon Landing": (ts.utc(1969, 7, 20, 20, 17), 2012, 15, 5, 40373849889636),
    "Ugarit Eclipse": (ts.utc(-1222, 3, 5, 13, 20), -1180, 44, 3, 15353849892318),
    "Distant Past": (ts.utc(-9000, 1, 1), -8958, 35, 3, 53753849896788),
    "Far Future": (ts.utc(3000, 1, 1), 3042, 36, 1, 53780849911272),
}


@pytest.mark.parametrize("test_name", TEST_CASES.keys())
def test_ucy_conversions(test_name):
    """Test UCY calendar conversions"""
    jd, exp_year, exp_week, exp_day, exp_nano = TEST_CASES[test_name]

    year, week, day, nano = to_parts(jd.tt)
    ucy_string = to_ucy(jd.tt)
    iso_string = jd.utc_iso()
    unix_seconds = round((jd.tt - 2440587.5) * 86400)

    columns = [
        "ucy_string",
        "desc",
        "ucy",
        "tt",
        "iso",
        "unix",
        "year",
        "week",
        "day",
        "nano",
    ]
    values = [
        ucy_string,
        test_name,
        ucy_string,
        jd.tt,
        iso_string,
        unix_seconds,
        year,
        week,
        day,
        nano,
    ]

    print()
    for column, value in zip(columns, values):
        print(f"  {column}: {value}")

    assert year == exp_year, f"Year mismatch for {test_name}"
    assert week == exp_week, f"Week mismatch for {test_name}"
    assert day == exp_day, f"Day mismatch for {test_name}"
    assert nano == exp_nano, f"Nano mismatch for {test_name}"
