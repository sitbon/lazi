from lazi.core.record import SpecRecord
from lazi.core.loader import Loader
from lazi.core.finder import Finder

__all__ = "SpecRecord", "Loader", "Finder", "RECORD"

RECORD = SpecRecord.RECORD

Finder.install()
