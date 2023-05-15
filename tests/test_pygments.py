

def test_pygments_formatter_auto():
    """Pytest failure while running test_rih_import_auto().
    """
    from lazi.util import debug
    import lazi.auto
    from lazi.core import uninstall

    debug.trace("-> from pygments.formatters.terminal import TerminalFormatter ->")
    from pygments.formatters.terminal import TerminalFormatter
    debug.trace("^- from pygments.formatters.terminal import TerminalFormatter -^")

    uninstall()


def test_pygments_formatter_ctxt():
    from lazi.util import debug
    from lazi.core import Finder

    with Finder():
        debug.trace("-> from pygments.formatters.terminal import TerminalFormatter ->")
        from pygments.formatters.terminal import TerminalFormatter
        debug.trace("^- from pygments.formatters.terminal import TerminalFormatter -^")
