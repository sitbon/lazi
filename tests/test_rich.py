

def test_rich_fn_import_ctx():
    from lazi.util import debug
    from lazi.core.finder import Finder

    with Finder() as finder:
        debug.trace("-> setup() ->")

        def setup():
            from rich import console as rc, pretty, traceback
            debug.trace("^- from rich import console as rc, pretty, traceback -^")
            debug.trace("-> console = rc.Console(color_system='256', force_terminal=True) ->")
            console = rc.Console(color_system="256", force_terminal=True)
            debug.trace("^- console = rc.Console(color_system='256', force_terminal=True) -^")
            debug.trace("-> pretty.install(console=console) ->")
            pretty.install(console=console)
            debug.trace("^- pretty.install(console=console) -^")
            debug.trace("-> traceback.install(console=console) ->")
            traceback.install(console=console)
            debug.trace("^- traceback.install(console=console) -^")

        setup()
        debug.trace("^- setup() -^")

    finder.invalidate_caches()
