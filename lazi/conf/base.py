"""Base project configuration.
"""
__meta__ = dict(                        # Internal configuration for <root>.conf.conf (cannot override elsewhere).
    root="lazi",                        # - Root namespace package name.
)                                       # See conf.py for more options.
#
TRACE: int = 0                          # Enable debug traces. Currently using levels 0-4.
#                                       # - Tracing relies on __debug__ and asserts, so -O will disable completely.
AUTO_AUTO: bool = True                  # Automatically install when importing lazi.auto.
CORE_AUTO: bool = False                 # Automatically install when importing lazi.core.
#
NO_HOOK: bool = False                   # Disable all spec loader hooks.
NO_HOOK_STD: bool = False               # Disable spec loader hooking for stdlib modules.
NO_HOOK_BI: bool = False                # Disable spec loader hooking for built-in modules.
NO_LAZY_LOAD: bool = False              # Next call to exec_module() skips lazy loading.
#
INVAL_SOFT: bool = False                # Keep modules in sys.modules after cache invalidation.
INVAL_GC: bool = (not INVAL_SOFT)       # Enable garbage collection on cache invalidation.
#                                       # - Only makes sense if INVAL_SOFT is False.
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
    and key.isupper()                   # along with __meta__["keys"] and __meta__["root"] as a prefix (TBD).
}
