"""Base project configuration.
"""

__meta__ = dict(                        # Internal configuration for <root>.conf.conf (cannot override elsewhere).
    root="lazi",                        # - Root namespace package name.
)                                       # See conf.py for more options.


DEBUG_TRACING: int = 0                  # Enable debug traces.

LAZI_AUTO_INSTALL: bool = True          # Automatically install when importing lazi.auto.
CORE_AUTO_INSTALL: bool = False         # Automatically install when importing lazi.core.

SPECR_KEEP_EMPTY: bool = False          # Keep records without a spec.
SPECR_KEEP_0HOOK: bool = False          # Keep records without a hook.
SPECR_HOOK_STDBI: bool = False          # Hook stdlib modules.

LOADER_AUTO_DEPS: bool = True          # Also load dependent imports when loading a module.

LOADER_FAKE_ATTR: tuple = (             # Attributes to fake and avoid loading a module. (__class__ is always faked.)
    "__spec__",                         # - These are the values that the Loader class currently knows how to fake.
    "__loader__",                       # - All: https://docs.python.org/3/reference/import.html#import-related-module-attributes
    "__name__",                         # - This is always present in the module and reliably known in advance.
    "__package__",                      # - "The value of __package__ is expected to be the same as __spec__.parent."
    "__file__",                         # - Approximated(?) by the module's spec.origin if spec.has_location.
    "__path__",                         # - Approximated(?) by the module's spec.submodule_search_locations if not None.
                                        #   - Current faking method is either unreliable or necessary... results have varied.
)

CONF_NO_CACHING: bool | None = None     # Disable caching of conf vars.
#                                         - None: Use the default caching behavior, which will disable
#                                                 caching if `lazi.core` is already present in sys.modules
#                                                 when lazi.conf.conf is imported.
