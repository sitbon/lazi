#!/usr/bin/env python
import os
import sys
import pytest
import _lazi


def setup():
    # from rich import console as rc, pretty, traceback
    # console = rc.Console(color_system="256", force_terminal=True)
    # pretty.install(console=console)
    # traceback.install(console=console)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_django.web.settings")

    import django
    # print(lazi.used_count(), len(lazi.RECORD), len(sys.modules))

    django.setup()


@pytest.mark.skip(reason="Not fully implemented yet")
@_lazi.param
@pytest.mark.parametrize("argv", [
    ["manage.py", "--help"],
    # ["manage.py", "migrate", "--fake"],
    # ["manage.py", "runserver", "--nothreading", "--noreload"],
])
def test_django_main(use_lazi: bool | None, argv: list):
    if use_lazi is not False:
        return _lazi.test(use_lazi, test_django_main, argv)

    import lazi.core as lazi

    stdout = sys.stdout
    # sys.stdout = sys.stderr = open("/dev/null", "w")

    setup()

    from tests.test_django import web
    from tests.test_django.web import settings
    sys.modules["web"] = web

    from django.core.management import execute_from_command_line

    execute_from_command_line(argv)

    print(lazi.used_count(), len(lazi.RECORD), len(sys.modules), file=stdout)


@pytest.mark.skip(reason="Not fully implemented yet")
def test_get_packages():
    setup()
    import django.template.backends.django
    django.template.backends.django.get_installed_libraries()


if __name__ == "__main__":
    test_django_main(True, sys.argv)
