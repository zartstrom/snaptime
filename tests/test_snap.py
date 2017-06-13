

from datetime import datetime
import pytest
import pytz

from snaptime import snap, snap_tz
from snaptime.main import parse, get_unit, SnapParseError, SnapUnitError


CET = pytz.timezone("Europe/Berlin")


# pylint: disable=bad-whitespace


@pytest.mark.parametrize("input_time,rel_time,output_time", [
    (datetime(2016, 10, 20, 12),        "-0d@d+1h",         datetime(2016, 10, 20, 1)),
    (datetime(2016, 10, 20, 12),        "-0d@d+2h",         datetime(2016, 10, 20, 2)),
    (datetime(2016, 10, 20, 12),        "-1d@d+1h",         datetime(2016, 10, 19, 1)),
    (datetime(2016, 10, 20, 12),        "-1d@d+2h",         datetime(2016, 10, 19, 2)),
    (datetime(2016,  6,  5,  3),        "-2d@d+12h",        datetime(2016,  6,  3, 12)),
    (datetime(2016,  6,  5,  3),        "-2d@d-12h",        datetime(2016,  6,  2, 12)),
    (datetime(2016, 10, 20, 12, 0, 40), "-5m@min",          datetime(2016, 10, 20, 11, 55, 0)),
    (datetime(2016, 10, 20, 12, 0, 45), "-6minutes@minute", datetime(2016, 10, 20, 11, 54, 0)),
    (datetime(2016, 10, 20, 12),        "-15m@m",           datetime(2016, 10, 20, 11, 45)),
    (datetime(2016, 10, 20, 12, 33),    "-0h@h",            datetime(2016, 10, 20, 12)),
    (datetime(2016, 10, 20, 12, 33),    "-1hour@h",         datetime(2016, 10, 20, 11)),
    (datetime(2016, 10, 20, 12, 33),    "-2hours@hours",    datetime(2016, 10, 20, 10, 0)),
    (datetime(2016, 10, 20, 12, 33),    "-27h@h",           datetime(2016, 10, 19, 9)),
    (datetime(2016, 10, 20, 12),        "-14d@d",           datetime(2016, 10, 6)),
    (datetime(2016, 10, 20, 12),        "-7day@day",        datetime(2016, 10, 13)),
    (datetime(2016, 10, 20, 12),        "-15days@days",     datetime(2016, 10, 5)),
    (datetime(2016, 10, 20, 12),        "-23d@d",           datetime(2016, 9, 27)),
    (datetime(2016, 10, 20, 12),        "-1mon@mon",        datetime(2016, 9, 1)),
    (datetime(2016, 10, 20, 12, 33),    "-1d@h",            datetime(2016, 10, 19, 12)),
    (datetime(2016, 10, 20, 12, 44),    "-5days@h",         datetime(2016, 10, 15, 12)),
    (datetime(2016, 10, 20, 12, 55),    "-7days@hours",     datetime(2016, 10, 13, 12)),
    (datetime(2016, 2, 11, 1),          "-1d@d",            datetime(2016, 2, 10, 0)),
    (datetime(2016, 2, 11, 1),          "@d",               datetime(2016, 2, 11, 0)),
    (datetime(2016, 2, 11, 0, 0, 7, 12),"@s",               datetime(2016, 2, 11, 0, 0, 7)),
    # daylight saving time switches on 30-10-2016 and 26-03-2017
    (datetime(2016, 10, 31, 12),        "-0month@month",    datetime(2016, 10, 1)),
    (datetime(2016, 10, 31, 12),        "-1month@month",    datetime(2016, 9, 1)),
    (datetime(2016, 10, 30, 12),        "@day",             datetime(2016, 10, 30)),
    (datetime(2017, 3, 26, 12),         "@day",             datetime(2017, 3, 26)),
    (datetime(2017, 3, 28),             "@month",           datetime(2017, 3, 1)),
    (datetime(2016, 10, 31, 12),        "-4y@y",            datetime(2012, 1, 1)),
    # week stuff
    (datetime(2016, 5, 9, 11),          "@w2",              datetime(2016, 5, 3, 0)),
    (datetime(2016, 5, 9, 11),          "@w3",              datetime(2016, 5, 4, 0)),
    (datetime(2016, 5, 9, 11),          "-1w@w",            datetime(2016, 5, 1, 0)),
    (datetime(2016, 10, 20, 12),        "-0w@w1",           datetime(2016, 10, 17)),
    (datetime(2016, 10, 20, 12),        "-2w@w2",           datetime(2016, 10, 4)),
    (datetime(2016, 10, 20, 12),        "-1w@w1",           datetime(2016, 10, 10)),
    (datetime(2016, 10, 20, 12),        "-1w@w2",           datetime(2016, 10, 11)),
    (datetime(2016, 10, 20, 12),        "-3w@w2",           datetime(2016, 9, 27)),
    (datetime(2016, 5, 9, 11),          "-1w@w4",           datetime(2016, 4, 28, 0))
])
def test_compare_begin_recalc(input_time, rel_time, output_time):
    # timezone unaware
    assert snap(input_time, rel_time) == output_time

    # timezone aware
    res = snap_tz(CET.localize(input_time), rel_time, CET)
    assert res == CET.localize(output_time)
    assert res.replace(tzinfo=None) == output_time


def test_parse_instruction():
    instr = "-3m@h+3d@d+3w@mon+1y+3h+4s"

    nof_units = parse(instr)
    assert len(nof_units) == 9


def test_empty_instruction():
    instr = ""
    dttm = datetime(2016, 7, 17, 15, 17, 0)
    assert dttm == snap(dttm, instr)


@pytest.mark.parametrize("string,result", [
    ("s", "seconds"),
    ("sec", "seconds"),
    ("secs", "seconds"),
    ("second", "seconds"),
    ("seconds", "seconds"),
    ("m", "minutes"),
    ("min", "minutes"),
    ("minute", "minutes"),
    ("minutes", "minutes"),
    ("h", "hours"),
    ("hr", "hours"),
    ("hrs", "hours"),
    ("hour", "hours"),
    ("hours", "hours"),
    ("d", "days"),
    ("day", "days"),
    ("days", "days"),
    ("weeks", "weeks"),
    ("w", "weeks"),
    ("week", "weeks"),
    ("mon", "months"),
    ("month", "months"),
    ("months", "months"),
    ("y", "years"),
    ("yr", "years"),
    ("yrs", "years"),
    ("year", "years"),
    ("years", "years"),
])
def test_get_unit(string, result):
    assert get_unit(string) == result


DTTM = datetime(2016, 7, 17, 15, 17, 0)


@pytest.mark.parametrize("instruction,bad_rest", [
    ("???", "???"),
    ("+2d@w+4&", "+4&"),
    ("+2d@w+4&+3y", "+4&+3y"),
])
def test_parse_error(instruction, bad_rest):
    with pytest.raises(SnapParseError) as exc:
        snap(DTTM, instruction)
    assert "'%s'" % instruction in exc.value.message
    assert "'%s'" % bad_rest in exc.value.message


@pytest.mark.parametrize("instruction,bad_unit", [
    ("+1m@xx-3days", "xx"),
    ("+2d@w+4unknown", "unknown")
])
def test_unit_error(instruction, bad_unit):
    with pytest.raises(SnapUnitError) as exc:
        snap(DTTM, instruction)

    assert "'%s'" % bad_unit in exc.value.message


@pytest.mark.parametrize("instruction,bad_weekday", [
    ("+1m@w8-3days", "8"),
    ("+2d@w12+4unknown", "12")
])
def test_bad_weekday(instruction, bad_weekday):
    with pytest.raises(SnapParseError) as exc:
        snap(DTTM, instruction)

    assert "'%s'" % bad_weekday in exc.value.message


@pytest.mark.parametrize("input_time,rel_time,output_time", [
    (datetime(2017, 3, 26, 3, 30),        "-1h@h",         datetime(2017, 3, 26, 1, 0)),
    (datetime(2017, 3, 26, 3, 30),        "@h",            datetime(2017, 3, 26, 3, 0)),
    (datetime(2017, 3, 26, 3, 30),        "-1d@d",         datetime(2017, 3, 25, 0, 0)),
    (datetime(2017, 3, 26, 3, 30),        "@d",            datetime(2017, 3, 26, 0, 0)),
])
def test_snap_tz_summertime(input_time, rel_time, output_time):
    loc_input_time = CET.localize(input_time)
    loc_output_time = CET.localize(output_time)
    assert snap_tz(loc_input_time, rel_time, CET) == loc_output_time


### new with tzinfo ###

@pytest.mark.parametrize("input_time,rel_time,output_time", [
    (CET.localize(datetime(2016, 10, 30, 2, 30), is_dst=True),  "-1h@h", CET.localize(datetime(2016, 10, 30, 1, 0))),
    (CET.localize(datetime(2016, 10, 30, 2, 30), is_dst=False), "-1h@h", CET.localize(datetime(2016, 10, 30, 2, 0), is_dst=True)),  # pylint: disable=line-too-long
    (CET.localize(datetime(2016, 10, 30, 2, 30), is_dst=True),  "@h",    CET.localize(datetime(2016, 10, 30, 2, 0), is_dst=True)),  # pylint: disable=line-too-long
    (CET.localize(datetime(2016, 10, 30, 2, 30), is_dst=False), "@h",    CET.localize(datetime(2016, 10, 30, 2, 0), is_dst=False)),  # pylint: disable=line-too-long

    (CET.localize(datetime(2016, 10, 30, 3, 30)),  "-1h@h", CET.localize(datetime(2016, 10, 30, 2, 0), is_dst=False)),
    (CET.localize(datetime(2016, 10, 30, 3, 30)),  "@h",    CET.localize(datetime(2016, 10, 30, 3, 0))),

    (CET.localize(datetime(2016, 10, 30, 2, 30), is_dst=True),  "-2h@h", CET.localize(datetime(2016, 10, 30, 0, 0))),
    (CET.localize(datetime(2016, 10, 30, 2, 30), is_dst=False), "-2h@h", CET.localize(datetime(2016, 10, 30, 1, 0))),
])
def test_snap_tz_wintertime(input_time, rel_time, output_time):
    assert snap_tz(input_time, rel_time, CET) == output_time
