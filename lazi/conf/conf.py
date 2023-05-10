"""Default configuration for Lazi.
"""

SPECR_KEEP_EMPTY: bool = False      # Keep records without a spec.
SPECR_KEEP_0HOOK: bool = False      # Keep records without a hook.
SPECR_KEEP_STACK: bool = True       # Keep import stacks in records.
SPECR_HOOK_STDLI: bool = False      # Hook stdlib modules.

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
            dic[key] = getattr(module, key)

    # for key in keys:
    #     setattr(namespace, key, dic[key])


__load()
