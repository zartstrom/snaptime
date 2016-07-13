coming soon ...


Manipulate a timestamp with a simple syntax.

Inspired by splunks relative time modifiers, see dull docs [here](http://docs.splunk.com/Documentation/Splunk/latest/SearchReference/SearchTimeModifiers#How_to_specify_relative_time_modifiers).

Usecases:
If have a datetime object and

1. go some time units back

2. calculate the beginning of the minute, hour, day, week etc.

3. combine both operations

Example:

```python
from datetime import datetime
from snaptime import snap
dt = datetime(2016, 7, 30, 15, 23, 59)
snap(dt, "-3d@d")
datetime(2016, 7, 26)
```



