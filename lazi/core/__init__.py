import lazi as __namespace__
from lazi.conf import conf
from .record import SpecRecord
from .loader import Loader
from .finder import Finder

__all__ = "conf", "SpecRecord", "Loader", "Finder", "RECORD", "tree", "lazy", "record", "used", "used_count"

RECORD = SpecRecord.RECORD

tree = SpecRecord.deps_tree

lazy = Finder.Import

record = Finder.ImportRecord

used = lambda: (_ for _ in RECORD.values() if _.used)  # noqa
used_count = lambda: sum(1 for _ in used())  # noqa

if conf.CORE_AUTO_INSTALL:
    Finder.install()

for _ in __all__:
    setattr(__namespace__, _, globals()[_])
del _
