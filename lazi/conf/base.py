"""Base project configuration.
"""

__meta__ = dict(                        # Internal configuration for <root>.conf.conf (cannot override elsewhere).
    root="lazi",                        # - Root namespace package name.
)                                       # See conf.py for more options.

DEBUG_TRACING: int = 0                  # Enable debug traces.

LAZI_AUTO_INSTALL: bool = True          # Automatically install when importing lazi.auto.
CORE_AUTO_INSTALL: bool = False         # Automatically install when importing lazi.core.
FORCE_LOAD_MODULE: bool = False         # Immediately call exec_module() on imported modules.
NO_STDLIB_MODULES: bool = True          # Disable loader hooking for stdlib modules.
DISABLE_LOAD_HOOK: bool = False         # Disable all loader hooks.
NO_DICT_LAZY_ATTR: bool = True          # Trigger exec_module() on __dict__ access.

CONF_NO_CACHING: bool | None = None     # Disable caching of conf vars.
#                                         - None: Use the default caching behavior, which will disable
#                                                 caching if `lazi.core` is already present in sys.modules
#                                                 when lazi.conf.conf is imported.
