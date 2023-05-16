from lazi.conf import conf as _conf
from .finder import Finder, __finder__

__all__ = (
    "Finder", "lazi", "lazy",
)

conf = _conf
lazi = __finder__
lazy = lazi.lazy

if _conf.CORE_AUTO_INSTALL:
    __finder__.__enter__()

for _ in __all__:
    setattr(_conf.__root__, _, globals()[_])
del _
