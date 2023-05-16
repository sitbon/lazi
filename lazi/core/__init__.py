"""
TODO:
"""
from lazi.conf import conf as _conf
from .finder import Finder, __finder__

__all__ = (
    "Finder", "__finder__",
    "lazi", "lazy", "install", "uninstall",
)

conf = _conf
lazi = __finder__
lazy = lazi.lazy
install = lazi.install
uninstall = lazi.uninstall


if _conf.CORE_AUTO_INSTALL:
    install()

for _ in __all__:
    setattr(_conf.__root__, _, globals()[_])
del _
