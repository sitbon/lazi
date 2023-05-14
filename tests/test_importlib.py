import pytest
from types import ModuleType
import importlib
import _lazi


@_lazi.param
@pytest.mark.parametrize("name, package, expected_type", [
    ("os", None, ModuleType),
    ("os.path", None, ModuleType),
    ("<bad>", None, ModuleNotFoundError),
    ("idna", "requests.packages", ModuleType),
    ("django.test", None, ModuleType),
    ("test", "django", ModuleType),
    ("pandas.core.nanops", None, ModuleType),
    ("django.db.models.aggregates", "django.db.", ModuleType),
])
def test_import_module(use_lazi, name, package, expected_type):
    if use_lazi is not False:
        return _lazi.test(use_lazi, test_import_module, name, package, expected_type)

    if issubclass(expected_type, Exception):
        with pytest.raises(expected_type):
            importlib.import_module(name, package)
    else:
        assert issubclass(type(importlib.import_module(name)), expected_type)

    return

