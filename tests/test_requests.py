import pytest


def test_requests_parse_dict_header():
    from lazi.util import debug
    from lazi.core.finder import Finder

    with Finder() as finder:
        debug.trace("-> from requests.utils import parse_dict_header ->")
        from requests.utils import parse_dict_header
        debug.trace("^- from requests.utils import parse_dict_header -^")

    finder.invalidate_caches()


@pytest.mark.skip(reason="Not using presto to remove Python 3.11 dependency.")
def test_requests_presto_import():
    from lazi.util import debug
    from lazi.core.finder import Finder

    with Finder() as finder:
        debug.trace("-> from presto import Presto ->")
        from presto import Presto
        debug.trace("^- from presto import Presto -^")
        debug.trace("-> p = Presto('https://httpbin.org') ->")
        p = Presto("https://httpbin.org")
        debug.trace("^- p = Presto('https://httpbin.org') -^")
        finder.invalidate_caches()
