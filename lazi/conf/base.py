"""Base project configuration.
"""
__meta__ = dict(                        # Internal configuration for <root>.conf.conf (cannot override elsewhere).
    root="lazi",                        # - Root namespace package name.
)                                       # See conf.py for more options.
#
#
TRACE: int = 0                          # Enable debug traces. Currently using levels 0-4.
#                                       # - Tracing relies on __debug__ and asserts, so `python -O` will disable completely.
#
NO_LAZY: int = 1                        # Hook loaders, but skip lazy loading.
#                                       # - 0: Lazy load all modules.
#                                       # - 1: Swap out (un-proxy) modules after lazy loading.
#                                       # - 2: Skip lazy loading.
#                                       # - 3: Skip lazy loading, and unwrap the module as well.
#                                       # - 4: Skip lazy loading, and unhook the loader as well.
#
LAZY: dict[str, int | str] = {}         # Specify loading behavior for specific modules (regex name -> NO_LAZY level).
#                                       # - Currently, `conf` does not merge dicts, so this must be set accordingly.
#                                       # - See `lazy.py` for the package defaults.
#
NO_HOOK: bool = False                   # Disable all spec loader hooks.
NO_HOOK_STD: bool = False               # Disable spec loader hooking for stdlib modules.
NO_HOOK_BI: bool = False                # Disable spec loader hooking for built-in modules.
NO_CHECK_STD_BI: bool = True            # Disable stdlib/built-in module checks (prevents autoloading of sysconfig data).
#                                       # - This renders NO_HOOK_STD and NO_HOOK_BI ineffective, and simply disables
#                                       #   the display of stdlib/built-in module tags (S/B) in the debug traces.
#
AUTO_AUTO: bool = True                  # Automatically install when importing lazi.auto.
CORE_AUTO: bool = False                 # Automatically install when importing lazi.core.
#
CONTEXT_INVALIDATION: bool = False      # Call invalidate_caches() when exiting a `with Finder()` statement.
#
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
