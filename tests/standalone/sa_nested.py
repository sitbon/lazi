import os

AUTO = int(os.environ.get('AUTO', '0'))


def do_imports(lazi_):
    # with lazi_:
    #     from rich import console as rc, pretty, traceback
    #     console = rc.Console(color_system="256", force_terminal=True)
    #     pretty.install(console=console)
    #     traceback.install(console=console)

    # from pygments.formatters.terminal import TerminalFormatter
    django = lazi_.lazy("django")
    version = django.VERSION
    test = lazi_.lazy("django.test")
    TestCase = test.TestCase
    from django.conf import settings
    from django.core.management import call_command


if AUTO:
    from lazi.auto import lazi, Finder

    def nested():
        with lazi:
            with Finder():
                do_imports(lazi)

    with lazi, Finder(), Finder():
        nested()


else:
    from lazi.core import lazi

    with lazi:
        def nested():
            do_imports(lazi)

        nested()
