import pytest
from types import ModuleType
import importlib


@pytest.mark.parametrize("attr, name, package, expected_type", [
    ("path", "os", None, ModuleType),
    ("split", "os.path", None, ModuleType),
    ("VERSION", "django", None, ModuleType),
    (None, "<bad>", None, ModuleNotFoundError),
    (None, "idna", "requests.packages", ModuleType),
    ("TestCase", "django.test", None, ModuleType),
    (None, "test", "django", ModuleType),
    (None, "pandas.core.nanops", None, ModuleType),
    (None, "django.db.models.aggregates", "django.db.", ModuleType),
])
def test_import_module(attr, name, package, expected_type):
    from lazi.util.debug import track, info
    from lazi.core import lazi

    with lazi, track(f"import {name}{f'[.{attr}]' if attr else ''}"):
        if issubclass(expected_type, Exception):
            with pytest.raises(expected_type):
                importlib.import_module(name, package)
        else:
            module = importlib.import_module(name, package)
            if attr is not None:
                with track(f"getattr({name}, {attr})"):
                    value = getattr(module, attr)
                    info(f"value: {repr(value)}")
            assert issubclass(type(module), expected_type)

    lazi.invalidate_caches()
