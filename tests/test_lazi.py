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
    assert lazi.Finder.refs == 2, lazi.Finder.refs
    assert lazi.uninstall() is lazi.Finder()
    assert lazi.uninstall() is None


def test_lazi_context_normal():
    import lazi.core as lazi

    with lazi.context():
        with _lazi.ensure():
            assert lazi.used(), lazi.Finder.refs


def test_lazi_context_lazy():
    import lazi.core as lazi

    with lazi.context():
        with _lazi.ensure(lazy=True):
            assert lazi.used(), lazi.Finder.refs


@pytest.mark.parametrize('use_lazi', (True,))
def test_lazi_runner_direct(use_lazi, _use_lazi=...):
    if use_lazi is not False:
        return _lazi.test(use_lazi, test_lazi_runner_direct, _use_lazi=use_lazi)

    with _lazi.ensure() as (lazi, mod):
        lazi_ = _lazi.core()

        assert lazi is lazi_, (lazi, lazi_)

        assert lazi.Finder.instance is lazi.Finder(), lazi.Finder.refs

        if _use_lazi is not None:
            assert lazi.Finder.refs == 1, lazi.Finder.refs

        assert list(lazi.used()), 0


@_lazi.param
def test_lazi_runner_param(use_lazi, _use_lazi=...):
    if use_lazi is not False:
        return _lazi.test(use_lazi, test_lazi_runner_param, _use_lazi=use_lazi)

    assert _use_lazi is not False or _use_lazi is ...

    with _lazi.ensure() as (lazi, mod):
        assert list(lazi.used()) or _use_lazi is ..., lazi.Finder.refs
