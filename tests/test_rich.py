import _lazi


@_lazi.param
def test_rich_fn_import(use_lazi):
    if use_lazi is not False:
        import lazi.auto

    def setup():
        from rich import console as rc, pretty, traceback
        console = rc.Console(color_system="256", force_terminal=True)
        pretty.install(console=console)
        traceback.install(console=console)

    setup()
