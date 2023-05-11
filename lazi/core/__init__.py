import lazi as __namespace__
from lazi.conf import conf
from .record import SpecRecord
from .loader import Loader
from .finder import Finder

__all__ = "conf", "SpecRecord", "Loader", "Finder", "RECORD", "tree", "lazy", "record"

RECORD = SpecRecord.RECORD
tree = SpecRecord.deps_tree
lazy = Finder.Import
record = Finder.ImportRecord

if conf.CORE_AUTO_INSTALL:
    Finder.install()

for _ in __all__:
    setattr(__namespace__, _, globals()[_])
del _
