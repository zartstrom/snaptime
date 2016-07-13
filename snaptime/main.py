

from datetime import timedelta
from dateutil.relativedelta import relativedelta  # can handle months
import re


# see also
# http://docs.splunk.com/Documentation/Splunk/6.4.0/SearchReference/SearchTimeModifiers#How_to_specify_relative_time_modifiers
UNIT_LISTS = {
    "seconds": ["s", "sec", "secs", "second", "seconds"],
    "minutes": ["m", "min", "minute", "minutes"],
    "hours": ["h", "hr", "hrs", "hour", "hours"],
    "days": ["d", "day", "days"],
    "weeks": ["w", "week", "weeks"],
    "months": ["mon", "month", "months"],
    # "quarters": ["q", "qtr", "qtrs", "quarter", "quarters"],  # not supported by relativedelta
    "years": ["y", "yr", "yrs", "year", "years"]
}


def get_unit(string):
    assert string

    for unit, variants in UNIT_LISTS.iteritems():
        if string in variants:
            return unit

    raise ValueError("Unknown unit string <%s>" % string)


def truncate(datetime_, unit):
    if unit == "minutes":
        result = datetime_.replace(second=0, microsecond=0)
    elif unit == "hours":
        result = datetime_.replace(minute=0, second=0, microsecond=0)
    elif unit == "days":
        result = datetime_.replace(hour=0, minute=0, second=0, microsecond=0)
    elif unit == "weeks":
        weekday = datetime_.isoweekday()
        result = datetime_.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=-weekday)
    elif unit == "months":
        result = datetime_.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif unit == "years":
        result = datetime_.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    return result


def parse_timedelta(string):
    pattern = re.compile(r"^(?P<unary>[-+]?)(?P<number>\d+)(?P<unit>[a-zA-Z]+)$")
    match = pattern.match(string)
    groupdict = match.groupdict()

    mult = -1 if groupdict["unary"] == "-" else 1
    number = int(groupdict["number"]) if groupdict["number"] is not None else 1
    unit = get_unit(groupdict["unit"])
    return relativedelta(**{unit: mult * number})  # pylint: disable=star-args


def add_snap(datetime_, snap_string):
    pattern = re.compile(r"^@(?P<unit>[a-zA-Z]+)(?P<weekday>\d+)?$")
    match = pattern.match(snap_string)

    if not match:
        raise ValueError("Could not find valid snap time: '%s'" % snap_string)
    groupdict = match.groupdict()

    result = datetime_

    snap_unit = get_unit(groupdict["unit"])
    weekday = groupdict["weekday"]
    if weekday is not None and snap_unit == "weeks":
        result = result - timedelta((datetime_.isoweekday() - int(weekday)) % 7)
        result = truncate(result, "days")
    elif snap_unit == "weeks":
        result = result - timedelta((datetime_.isoweekday() - 0) % 7)
        result = truncate(result, "days")
    else:
        # normal case
        result = truncate(result, snap_unit)

    return result


def snap(scheduled_time, relative_time):
    """

    Calculates the actual datetime (begin or end) for a saved search from the scheduled time and relative time
    statement (dispatch.earliest_time or dispatch.latest_time)

    Args:
        relative_time (string): a relative time statement like "-1h@h"
        scheduled_time (datetime):
    Returns:
        datetime: The "sum" of scheduled time and the relative time

    Example:
        >>> from_relative_time("-1h@h", datetime(2016, 1, 1, 15, 30))
        datetime(2016, 1, 1, 14)
    """
    # delta_pattern = "([-+]?\d+[a-zA-Z]+)?"
    # snap_pattern = "@([a-zA-Z]+\d*)"
    pattern = re.compile(r"^(?P<prefix>[-+]?\d+[a-zA-Z]+)?(?P<snap>@[a-zA-Z]+\d*)(?P<postfix>[-+]?\d+[a-zA-Z]+)?")

    match = pattern.match(relative_time)

    if not match:
        raise ValueError("Could not find valid time statement in string: '%s'" % relative_time)

    groupdict = match.groupdict()

    assert groupdict["snap"]

    result = scheduled_time

    if "prefix" in groupdict and groupdict["prefix"] is not None:
        result = result + parse_timedelta(groupdict["prefix"])

    # do snap here:
    result = add_snap(result, groupdict["snap"])

    if "postfix" in groupdict and groupdict["postfix"] is not None:
        result = result + parse_timedelta(groupdict["postfix"])

    return result
