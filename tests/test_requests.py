import pytest
import _lazi


@_lazi.param
def test_requests_parse_dict_header(use_lazi):
    if use_lazi is not False:
        return _lazi.test(use_lazi, test_requests_parse_dict_header)

    from requests.utils import parse_dict_header


@_lazi.param
def test_requests_presto_import(use_lazi):
    if use_lazi is not False:
        return _lazi.test(use_lazi, test_requests_presto_import)

    from presto import Presto
    p = Presto("https://httpbin.org")
