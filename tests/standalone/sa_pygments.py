import os

AUTO = int(os.environ.get('AUTO', '0'))


if AUTO:
    import lazi.auto
    from pygments.formatters.terminal import TerminalFormatter

else:
    from lazi.core import Finder

    with Finder():
        from pygments.formatters.terminal import TerminalFormatter
