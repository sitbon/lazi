from lazi.conf import conf
from .record import SpecRecord
from .loader import Loader
from .finder import Finder

__all__ = (
    "conf", "SpecRecord", "Loader", "Finder",
    "RECORD", "used", "used_count", "tree",
    "lazy", "record", "context", "install", "uninstall",
)

RECORD = SpecRecord.RECORD
used = SpecRecord.RECORD_USED
used_count = SpecRecord.RECORD_USED_COUNT
tree = SpecRecord.deps_tree
lazy = Finder.lazy_module
record = Finder.lazy_record
context = Finder.context
install = Finder.install
uninstall = Finder.uninstall


if conf.CORE_AUTO_INSTALL:
    install()

for _ in __all__:
    setattr(conf.__root__, _, globals()[_])
del _
