
### snaptime

The snaptime package is about transforming timestamps simply.

It is inspired by splunks relative time modifiers, see their docs [here][splunk-docs].

### Examples

```python
>>> from datetime import datetime
>>> from snaptime import snap

>>> snap(datetime(2018, 10, 28, 23), "@d")
datetime.datetime(2018, 10, 28, 0, 0)

>>> snap(datetime(2018, 10, 28, 23), "+3h")
datetime.datetime(2018, 10, 29, 2, 0)

>>> snap(datetime(2018, 10, 28, 23), "+3h@d")
datetime.datetime(2018, 10, 29, 0, 0)

>>> snap(datetime(2018, 10, 28, 23), "+3h@d+15m")
datetime.datetime(2018, 10, 29, 0, 15)
```

### Motivating example:
Say Harry wants to send a letter and there is mailbox right to his door, which is cleared every day at 16:00h. The post delivers letters the next day at 11:00h. So given a datetime `t` - at which Harry throws the letter into the mailbox - when does the letter get delivered?

One straightforward implementation would be:

1. check whether `t` is before or after 16:00h
2. truncate hours, minutes and seconds
3. add 1 or 2 days (according step 1) plus 11h

This would take some lines of code, but with snaptime the solution would be a one-liner:

```python
from snaptime import snap
snap(t, "+8h@d+1d+11h")
```

In plain words this

1. adds 8 hours to `t` (+8h)
2. snaps to the beginning of the day (@d)
3. adds one day and 11h (+1d+11h)

### Two types of transformations

There are two types of transformations that can be chained freely in the snap function.

#### Snap Transformation

A snap transformation is written as `@<timeunit>`, which truncates to the given time unit. I.e. `@h` applied to a timestamp sets minutes, seconds and microseconds to zero. Snapping to seconds, minutes, days, months, years work the same way.
Further it is also possible to snap to weeks (`@w`), and even to specific week days (`@w0`, `@w1`, ..., `@w6` for Sunday, Monday, ..., Saturday).

#### Delta Transformation

A delta transformation (the name is kind of an overstatement..) works analogously to the `datetime.timedelta` object from the standard library. A signed number ([+-]\d+) and a time unit indicate the change on the given timestamp.

### Time Units

There are several strings for each time unit that indicate that same time unit. Here is the full table:

| Unit | Equal notations |
|:---:|:---|
|seconds| s, sec, secs, second, seconds|
|minutes| m, min, minute, minutes|
|hours| h, hr, hrs, hour, hours|
|days| d, day, days|
|weeks| w, week, weeks|
|months| mon, month, months|
|years| y, yr, yrs, year, years|

For a given datetime `t` i.e. this assertion holds true

```python
assert snap(t, "-3hours@day+2weeks@month") == snap(t, "-3hrs@d+2w@mon")
```

### Timezone aware timestamps

There is also a function snap_tz, that handles daylight saving time switches.

```python
>>> from datetime import datetime
>>> from snaptime import snap, snap_tz

>>> dttm = CET.localize(datetime(2017, 3, 26, 3, 44))
>>> dttm
datetime.datetime(2017, 3, 26, 3, 44, tzinfo=<DstTzInfo 'Europe/Berlin' CEST+2:00:00 DST>)

>>> snap(dttm, "+3h")
datetime.datetime(2017, 3, 26, 6, 44, tzinfo=<DstTzInfo 'Europe/Berlin' CEST+2:00:00 DST>)
>>> # Everything ok

>>> # .. but here is the danger zone
>>> snap(dttm, "@d")
datetime.datetime(2017, 3, 26, 0, 0, tzinfo=<DstTzInfo 'Europe/Berlin' CEST+2:00:00 DST>)
```

This probably not what we want. There is a daylight saving time switch at 2h. We most probably want this result:

```python
>>> CET.localize(datetime(2017, 3, 26))
datetime.datetime(2017, 3, 26, 0, 0, tzinfo=<DstTzInfo 'Europe/Berlin' CET+1:00:00 STD>)
```

The resulting datetimes are different, as the tzinfo indicates (their epoch seconds differ by one hour). There is snap_tz to the rescue. It requires an additional timezone parameter and handles the situation correctly:

```python
>>> snap_tz(dttm, "@d", CET)
datetime.datetime(2017, 3, 26, 0, 0, tzinfo=<DstTzInfo 'Europe/Berlin' CET+1:00:00 STD>)
```

### Development

Running unit test

```bash
git clone https://github.com/zartstrom/snaptime
cd snaptime
mkvirtualenv --python=/usr/bin/python2 snaptime
pip install -r requirements.pip
py.test
```

Please feel free to send comments and/or pull requests.

[splunk-docs]: http://docs.splunk.com/Documentation/Splunk/latest/SearchReference/SearchTimeModifiers#How_to_specify_relative_time_modifiers
