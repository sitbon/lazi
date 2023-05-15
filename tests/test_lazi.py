import pytest
import _lazi


@pytest.mark.test_test
@_lazi.param
@pytest.mark.parametrize("test_func", [lambda use_lazi: None])
def test_test(use_lazi, test_func, *args, **kwds):
    assert _lazi.test(use_lazi, test_func, *args, **kwds) is None


def test_lazi_install():
    import lazi.core as lazi
    assert lazi.install() is lazi.install()
    assert lazi.__finder__.__refs__ == 2, lazi.__finder__.__refs__
    assert lazi.uninstall() is False
    assert lazi.uninstall() is True


@pytest.mark.skipif(not __debug__, reason="This module is only for testing.")
def test_lazi_context_normal():
    import lazi.core as lazi

    with lazi.context:
        ...
