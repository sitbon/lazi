from lazi.util.debug import track, info
from lazi.core.stat import Stat
from lazi.core import lazi


def test_pygments_formatter():
    with lazi:
        with track("import pygments"):
            info(Stat())
            from pygments.formatters.terminal import TerminalFormatter
            info(Stat())
