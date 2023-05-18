import pytest


def test_stat_django_test():
    from lazi.util.debug import track, log

    from lazi.core.stat import Stat
    from lazi.core import lazi

    with lazi:
        with track("import django.test"):
            log(Stat())
            import django.test as dt
            log(Stat())

        with track("TestCase = dt.TestCase"):
            TestCase = dt.TestCase
            log(Stat())


@pytest.mark.skip(reason="not working")
def test_stat_presto():
    from lazi.util.debug import track, log

    from lazi.core.stat import Stat
    from lazi.core import lazi

    with lazi:
        with track("import presto"):
            log(Stat())
            from presto import Presto
            log(Stat())

        with track("p = Presto('https://httpbin.org')"):
            p = Presto("https://httpbin.org")
            log(Stat())


def test_stat_nolazi_presto():
    from lazi.util.debug import track, log

    from lazi.core.stat import Stat

    with track("import presto"):
        log(Stat())
        from presto import Presto
        log(Stat())

    with track("p = Presto('https://httpbin.org')"):
        p = Presto("https://httpbin.org")
        log(Stat())
