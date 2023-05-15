import os

AUTO = int(os.environ.get('AUTO', '0'))


if AUTO:
    import lazi.auto
    from array import array

else:
    from lazi.core import Finder

    with Finder():
        from array import array
