"""Map of module name regexes to lazy loading modes.

Mode can either be an int, corresponding to `base.NO_LAZI`, or a string
corresponding to the same `lazi.core.spec.Spec.Level` names:
- "NONE" = -1
- "LAZY" = 0
- "LOAD" = 1
- "UNMO" = 2
- "UNLO" = 3
"""


LAZY: dict[str, int | str] = {

    r"^pandas\.core\.": "LOAD",

    r"^requests|^certifi|^presto": "LOAD",

}
