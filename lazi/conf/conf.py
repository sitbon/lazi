"""Default configuration for Lazi.
"""

DEBUG_TRACING: bool = False          # Enable debug traces.

SPECR_KEEP_EMPTY: bool = False      # Keep records without a spec.
SPECR_KEEP_0HOOK: bool = False      # Keep records without a hook.
SPECR_HOOK_STDBI: bool = False      # Hook stdlib modules.

LOADER_AUTO_DEPS: bool = True       # Also load dependent imports when loading a module.
LOADER_FAKE_ATTR: tuple = (         # Attributes to fake and avoid loading a module.
    "__spec__",                     # - These three are the values that the Loader class currently knows how to fake.
    "__loader__",                   # - All: https://docs.python.org/3/reference/import.html#import-related-module-attributes
    "__name__",
)


def __load():
    import sys
    from pkgutil import iter_modules
    from importlib import import_module
    import lazi.conf as namespace

    dic = sys.modules[__name__].__dict__
    keys = set(key for key in dic.keys() if not key.startswith("_") and key.isupper())

    for module_info in (mi for mi in iter_modules(namespace.__path__, namespace.__name__ + ".") if mi.name != __name__):
        module = import_module(module_info.name)

        for key in (key for key in keys if hasattr(module, key)):
            dic[key] = getattr(module, key)  # TODO (As Needed): Check type and merge accordingly.

    for key in keys:
        setattr(namespace, key, dic[key])


__load()
