from skyfield import almanac
from skyfield.api import Loader
import math

DAY_NS = 86_400_000_000_000
EPSILON_DAYS = 368.0
TROPICAL_YEAR_DAYS = 365.2421875  # octal: 0o555.174
WEEKS_PER_YEAR = TROPICAL_YEAR_DAYS / 8.0

_loader = Loader("~/.skyfield-data", verbose=False)
eph, ts = _loader("de431t.bsp"), _loader.timescale()
del _loader


def next_equinox(tt):
    """Find the next spring equinox after the given time.

    Args:
        tt: Terrestrial Time (TT) in Julian days

    Returns:
        TT of the next spring equinox in Julian days
    """
    t0 = ts.tt_jd(tt)
    t1 = ts.tt_jd(tt + EPSILON_DAYS)
    times, codes = almanac.find_discrete(t0, t1, almanac.seasons(eph))
    equinox = max(t.tt for t, c in zip(times, codes) if c == 0)
    return equinox


# Datum: Spring equinox after Caesar's death (March 21, 44 BCE ~9:04 AM UTC)
# We search from March 1st to ensure we find the correct equinox.
DATUM_TT = next_equinox(ts.utc(-43, 3, 1).tt)


def year_start(tt):
    """Find the year start boundary for the given time.

    The year start is determined by:
    1. Finding the spring equinox before or near tt
    2. Snapping that equinox to the nearest 8-day boundary from DATUM_TT
    3. If tt falls before that boundary, finding the previous year's boundary

    Args:
        tt: Terrestrial Time (TT) in Julian days

    Returns:
        TT of the year start boundary in Julian days
    """
    equinox = next_equinox(tt - EPSILON_DAYS)

    delta = equinox - DATUM_TT
    weeks = 0 if abs(delta) < 0.001 else math.floor(delta / 8.0)
    boundary = DATUM_TT + (weeks * 8.0)

    if tt < boundary:
        equinox = next_equinox(boundary - EPSILON_DAYS * 2)
        delta = equinox - DATUM_TT
        weeks = math.floor(delta / 8.0)
        boundary = DATUM_TT + (weeks * 8.0)

    return boundary


def to_parts(tt):
    """Convert TT (Terrestrial Time) to UCY calendar parts.

    Args:
        tt: Terrestrial Time (TT) in Julian days

    Returns:
        Tuple of (year, week, day, nano) where:
        - year: Year number (0 = datum year at March 21, 44 BCE)
        - week: Week within year (0-45)
        - day: Day within week (0-7, zero-indexed)
        - nano: Nanoseconds within day (0 to 86_399_999_999_999)
    """
    y_start = year_start(tt)

    delta = tt - y_start
    doy = math.floor(delta)
    week = doy // 8
    day = doy % 8
    nano = math.floor((delta - doy) * DAY_NS)

    weeks_from_datum = (y_start - DATUM_TT) / 8.0
    year = round(weeks_from_datum / WEEKS_PER_YEAR)

    return year, week, day, nano


def to_ucy(tt):
    """Convert TT to UCY octal string format.

    Args:
        tt: Terrestrial Time (TT) in Julian days

    Returns:
        String in format: year_week_day.fraction (all in octal)
        Example: "4024_30_2.1124"
    """
    year, week, day, nano = to_parts(tt)
    frac_int = (nano * 8**4) // DAY_NS

    year_oct = f"{year:o}".replace("-", "0")
    week_oct = f"{week:02o}"
    day_oct = f"{day:o}"
    frac_oct = f"{frac_int:04o}"

    return f"{year_oct}_{week_oct}_{day_oct}.{frac_oct}"


if __name__ == "__main__":
    print(f"Current UCY: {to_ucy(ts.now().tt)}")
