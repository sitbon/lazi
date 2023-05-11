DEBUG_TRACING: bool = False         # Enable debug traces.

LAZI_AUTO_INSTALL: bool = True      # Automatically install when importing lazi.auto.
CORE_AUTO_INSTALL: bool = False     # Automatically install when importing lazi.core.

SPECR_KEEP_EMPTY: bool = False      # Keep records without a spec.
SPECR_KEEP_0HOOK: bool = False      # Keep records without a hook.
SPECR_HOOK_STDBI: bool = False      # Hook stdlib modules.

LOADER_AUTO_DEPS: bool = True       # Also load dependent imports when loading a module.
LOADER_FAKE_ATTR: tuple = (         # Attributes to fake and avoid loading a module.
    "__spec__",                     # - These three are the values that the Loader class currently knows how to fake.
    "__loader__",                   # - All: https://docs.python.org/3/reference/import.html#import-related-module-attributes
    "__name__",
)
