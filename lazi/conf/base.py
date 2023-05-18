"""Base project configuration.
"""
__meta__ = dict(                        # Internal configuration for <root>.conf.conf (cannot override elsewhere).
    root="lazi",                        # - Root namespace package name.
)                                       # See conf.py for more options.
#
TRACE: int = 0                          # Enable debug traces. Currently using levels 0-4.
TRACEE: bool = False                     # Enable debug traces for loader exceptions when TRACE is 0.
#                                       # - Tracing relies on __debug__ and asserts, so -O will disable completely.
AUTO_AUTO: bool = True                  # Automatically install when importing lazi.auto.
CORE_AUTO: bool = False                 # Automatically install when importing lazi.core.
#
NO_HOOK: bool = False                   # Disable all spec loader hooks.
NO_LAZY: bool = False                   # Hook loaders, but skip lazy loading.
NO_HOOK_STD: bool = False               # Disable spec loader hooking for stdlib modules.
NO_HOOK_BI: bool = False                # Disable spec loader hooking for built-in modules.
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
__all__: list = [                       # Configuration keys that are allowed to be set.
    key for key in globals()            # - Not inherited or mutable.
    if not key.startswith("_")          # - Can be supplemented from __meta__['keys'].
    and key.isupper()
]
