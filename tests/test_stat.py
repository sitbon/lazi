import pytest


def test_stat_django_test():
    from lazi.util.debug import track, info

    from lazi.core.stat import Stat
    from lazi.core import lazi

    with lazi:
        with track("import django.test"):
            info(Stat())
            import django.test as dt
            info(Stat())

        with track("TestCase = dt.TestCase"):
            TestCase = dt.TestCase
            info(Stat())


# @pytest.mark.skip(reason="not working")
def test_stat_presto():
    from lazi.util.debug import track, info

    from lazi.core.stat import Stat
    from lazi.core import lazi

    with lazi:
        with track("import presto"):
            info(Stat())
            from presto import Presto
            info(Stat())

        with track("p = Presto('https://httpbin.org')"):
            p = Presto("https://httpbin.org")
            info(Stat())


def test_stat_nolazi_presto():
    from lazi.util.debug import track, info

    from lazi.core.stat import Stat

    with track("import presto"):
        info(Stat())
        from presto import Presto
        info(Stat())

    with track("p = Presto('https://httpbin.org')"):
        p = Presto("https://httpbin.org")
        info(Stat())
