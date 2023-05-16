"""Base project configuration.
"""
__meta__ = dict(                        # Internal configuration for <root>.conf.conf (cannot override elsewhere).
    root="lazi",                        # - Root namespace package name.
)                                       # See conf.py for more options.
#
DEBUG_TRACING: int = 0                  # Enable debug traces. Currently using levels 0-4.
#
LAZI_AUTO_INSTALL: bool = True          # Automatically install when importing lazi.auto.
CORE_AUTO_INSTALL: bool = False         # Automatically install when importing lazi.core.
FORCE_LOAD_MODULE: bool = False         # Immediately call exec_module() on imported modules.
NO_STDLIB_MODULES: bool = False         # Disable loader hooking for stdlib modules.
DISABLE_LOAD_HOOK: bool = False         # Disable all loader hooks.
SOFT_INVALIDATION: bool = False         # Keep modules in sys.modules after cache invalidation.
GARBAG_COLLECTION: bool = (             # Enable garbage collection on cache invalidation.
    not SOFT_INVALIDATION)              # - Only makes sense if SOFT_INVALIDATION is False.
#
#
CONF_NO_CACHING: bool | None = None     # Disable caching of conf vars.
#                                         - None: Use the default caching behavior, which will disable
#                                                 caching if `lazi.core` is already present in sys.modules
#                                                 when lazi.conf.conf is imported.
#
CONF_KEYS: set = {                      # Configuration keys that are allowed to be set.
    key for key in globals()            # - Can be inherited / changed, but support is untested.
    if not key.startswith("_")          # - envs.py does not support anything other than this base value,
    and key.isupper()                   # along with __meta__["keys"].
}
