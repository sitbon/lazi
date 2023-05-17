from lazi.util.debug import track, log
from lazi.core.stat import Stat
from lazi.core import lazi


def test_pygments_formatter():
    with lazi:
        with track("import pygments"):
            log(Stat())
            from pygments.formatters.terminal import TerminalFormatter
            log(Stat())
