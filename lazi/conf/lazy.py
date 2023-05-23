"""Map of module name regexes to lazy loading modes.

Mode can either be an int, corresponding to a `base.NO_LAZY` value, or a string
corresponding to the same `lazi.core.spec.Spec.Level` names:

# NONE - -1: Disable lazy loading (same effect as NO_HOOK).
# LAZY - 0: Lazy load all modules.
# SWAP - 1: Swap out (un-proxy) modules after lazy loading.
# LOAD - 2: Skip lazy loading.
# UNMO - 3: Skip lazy loading, and unwrap the module as well.
# UNLO - 4: Skip lazy loading, and unhook the loader as well.
"""


LAZY: dict[str, int | str] = {

    r"^pandas\.core\.|^pandas\._config": "UNLO",

    # r"^pandas": "LOAD",

    r"^requests\.utils|^certifi": "UNLO",

    r"^django\.(db\.models.*|conf.*|utils.*)": "UNLO",

}
