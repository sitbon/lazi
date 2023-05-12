import pytest
from types import ModuleType
import importlib


@pytest.mark.parametrize("use_lazi", [True, False, None])
@pytest.mark.parametrize("name, package, expected_type", [
    ("os", None, ModuleType),
    ("os.path", None, ModuleType),
    ("<bad>", None, ModuleNotFoundError),
    ("idna", "requests.packages", ModuleType),
])
def test_import_module(use_lazi, name, package, expected_type):
    match use_lazi:
        case True:  # Auto
            import lazi.auto
            return test_import_module(use_lazi=False, name=name, package=package, expected_type=expected_type)

        case None:  # Context
            from lazi.core import context
            with context():
                return test_import_module(use_lazi=False, name=name, package=package, expected_type=expected_type)

        case False:
            if issubclass(expected_type, Exception):
                with pytest.raises(expected_type):
                    importlib.import_module(name, package)
            else:
                assert issubclass(type(importlib.import_module(name)), expected_type)

            return

        case _:
            raise ValueError(f"Unknown use_lazi: {use_lazi!r}")

    assert False, "Unreachable"  # noqa
