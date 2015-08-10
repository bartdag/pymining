import sys

if sys.version_info[0] < 3:
    range = xrange  # noqa
else:
    range = range
