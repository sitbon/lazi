

def test_pygments_formatter():
    from lazi.util import debug
    from lazi.core import Finder

    with Finder():
        debug.trace("-> from pygments.formatters.terminal import TerminalFormatter ->")
        from pygments.formatters.terminal import TerminalFormatter
        debug.trace("^- from pygments.formatters.terminal import TerminalFormatter -^")
