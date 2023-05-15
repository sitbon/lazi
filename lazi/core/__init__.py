from lazi.conf import conf
from .finder import Finder, __finder__

__all__ = (
    "Finder", "__finder__",
    "lazy", "context", "install", "uninstall",
)


lazy = Finder.lazy
context = __finder__
install = Finder.install
uninstall = Finder.uninstall


if conf.CORE_AUTO_INSTALL:
    install()

for _ in __all__:
    setattr(conf.__root__, _, globals()[_])
del _
