"""Loading and unlading Lazi for tests.

Asserts here have side effects, so only __debug__ mode is supported (no -O).
"""
import sys
import pytest
import importlib
from contextlib import contextmanager


if not __debug__:
    raise ImportError("This module is only for testing.")


param = pytest.mark.parametrize('use_lazi', (False, True, None))


def core():
    if "lazi.core" in sys.modules:
        return sys.modules["lazi.core"]
    import lazi.core
    return sys.modules["lazi.core"]


def run(flag: bool | None, func, /, *args, **kwds):
    lazi = core()

    if flag is False:
        try:
            return func(*args, **kwds)
        finally:
            pass
            # To be implemented later:
            # import lazi.core
            # lazi.core.unload()

    if flag is True:
        while lazi.uninstall() is not None:
            pass
        lazi.install()
        try:
            return run(False, func, *args, **kwds)
        finally:
            assert lazi.uninstall() is None, lazi.Finder.refs

    assert flag is None, flag

    try:
        with lazi.context():
            return run(False, func, *args, **kwds)
    finally:
        assert lazi.Finder.refs == 0, lazi.Finder.refs


def test(use_lazi: bool | None, test_func, *args, **kwds):
    return run(use_lazi, test_func, False, *args, **kwds)


def module(name, package=None, lazi=None):
    if lazi is None:
        return importlib.import_module(name, package)

    assert package is None
    return lazi.lazy(name)


@contextmanager
def ensure(*, name="django", attr="VERSION", lazy=False, lazi=None):
    lazi = lazi or core()

    mod = module(name, lazi=lazi if lazy else None)

    getattr(mod, attr)

    assert hasattr(mod, attr), (name, attr)

    assert lazi.used(), lazi.Finder.refs

    try:
        yield lazi, mod
    finally:
        sys.modules.pop(mod.__name__.partition(".")[0], None)
