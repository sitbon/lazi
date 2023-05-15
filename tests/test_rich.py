

def test_rich_fn_import():
    from lazi.util import debug
    from lazi.core.finder import Finder

    with Finder() as finder:
        debug.trace("-> setup() ->")

        def setup():
            from rich import console as rc, pretty, traceback
            console = rc.Console(color_system="256", force_terminal=True)
            pretty.install(console=console)
            traceback.install(console=console)

        setup()
        debug.trace("^- setup() -^")
