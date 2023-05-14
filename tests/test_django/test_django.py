"""Automatic lazy loading example.
"""
import pytest
import _lazi


@_lazi.param
@pytest.mark.parametrize("lazy", (True, False))
@pytest.mark.parametrize("name, attr", (
    ("django", "VERSION"),
    ("django.test", "TestCase"),
    ("django.template", "Template"),
    ("django.db.models.functions", "math"),
    ("django.db.models.aggregates", "__all__"),
    # ("tlz", "comp"),
))
def test_django_imports(use_lazi, name, attr, lazy):
    if use_lazi is not False:
        return _lazi.test(use_lazi, test_django_imports, name, attr, lazy)

    with _lazi.ensure(name=name, attr=attr, lazy=lazy):
        pass
