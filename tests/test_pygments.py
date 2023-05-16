

def test_pygments_formatter_auto():
    """Pytest failure while running test_rih_import_auto().
    """
    from lazi.util import debug
    from lazi.auto import lazi

    debug.trace("-> from pygments.formatters.terminal import TerminalFormatter ->")
    from pygments.formatters.terminal import TerminalFormatter
    debug.trace("^- from pygments.formatters.terminal import TerminalFormatter -^")

    lazi.__exit__(None, None, None)


def test_pygments_formatter_ctxt():
    from lazi.util import debug
    from lazi.core import Finder

    with Finder():
        debug.trace("-> from pygments.formatters.terminal import TerminalFormatter ->")
        from pygments.formatters.terminal import TerminalFormatter
        debug.trace("^- from pygments.formatters.terminal import TerminalFormatter -^")
