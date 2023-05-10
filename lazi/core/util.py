import sys
from typing import Callable
from types import ModuleType
from importlib.machinery import ModuleSpec
import sysconfig
from pathlib import Path

from lazi.conf import conf


def is_stdlib_or_builtin(module: ModuleType | ModuleSpec) -> bool:
    if isinstance(module, ModuleType):
        spec = getattr(module, "__spec__", None)
        return (spec is None) or is_stdlib_or_builtin(spec)
    elif isinstance(module, ModuleSpec):
        origin = module.origin
        return (origin in (None, "built-in")) or Path(origin).is_relative_to(sysconfig.get_path("stdlib"))

    raise TypeError(f"Expected ModuleType or ModuleSpec, got {type(module)}")


def nofail(func: Callable, /, *args, **kwds):
    try:
        func(*args, **kwds)
    except Exception as exc:
        print(f"Exception when calling {func.__name__}(): {exc}", file=sys.stderr)


if conf.DEBUG_TRACING:
    def trace(*args, **kwds):
        kwds.setdefault("file", sys.stderr)
        print(*args, **kwds)

else:
    def trace(*args, **kwds):
        pass
