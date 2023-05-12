from types import ModuleType
from importlib.machinery import ModuleSpec
import sysconfig
from pathlib import Path

__all__ = "is_stdlib_or_builtin",


def is_stdlib_or_builtin(module: ModuleType | ModuleSpec) -> bool:

    if isinstance(module, ModuleType):
        return ((spec := getattr(module, "__spec__", None)) is None) or is_stdlib_or_builtin(spec)

    elif isinstance(module, ModuleSpec):
        return ((origin := module.origin) in (None, "built-in")) or \
            Path(origin).is_relative_to(sysconfig.get_path("stdlib"))

    raise TypeError(f"Expected ModuleType or ModuleSpec, got {type(module)}")
