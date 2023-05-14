import pytest
import _lazi


@_lazi.param
def test_pandas_libs_auto(use_lazi: bool | None):
    if use_lazi is not False:
        return _lazi.test(use_lazi, test_pandas_libs_auto)

    from pandas._libs import lib
