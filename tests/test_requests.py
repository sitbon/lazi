

def test_requests_parse_dict_header():
    from lazi.util import debug
    from lazi.core.finder import Finder

    with Finder():
        debug.trace("-> from requests.utils import parse_dict_header ->")
        from requests.utils import parse_dict_header
        debug.trace("^- from requests.utils import parse_dict_header -^")


def test_requests_presto_import():
    from lazi.util import debug
    from lazi.core.finder import Finder

    with Finder():
        debug.trace("-> from presto import Presto ->")
        from presto import Presto
        debug.trace("^- from presto import Presto -^")
        debug.trace("-> p = Presto('https://httpbin.org') ->")
        p = Presto("https://httpbin.org")
        debug.trace("^- p = Presto('https://httpbin.org') -^")
