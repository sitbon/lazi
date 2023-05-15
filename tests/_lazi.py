"""Loading and unlading Lazi for tests.

Asserts here have side effects, so only __debug__ mode is supported (no -O).
"""
import sys
import pytest
import importlib

from lazi.core import Finder

param = pytest.mark.parametrize('use_lazi', (False, True))

pytest.mark.skipif(not __debug__, reason="This module is only for testing.")


def run(flag: bool, func, /, *args, **kwds):
    finder = Finder()

    if not flag:
        return func(*args, **kwds)

    with finder:
        return run(False, func, *args, **kwds)


def test(use_lazi: bool | None, test_func, *args, **kwds):
    return run(use_lazi, test_func, False, *args, **kwds)


def module(name, package=None, finder=None):
    if finder is None:
        return importlib.import_module(name, package)

    assert package is None
    return finder.lazy(name)
