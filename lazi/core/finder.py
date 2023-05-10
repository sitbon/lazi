from __future__ import annotations

import sys
from importlib.util import find_spec
from importlib.machinery import ModuleSpec
from importlib.abc import MetaPathFinder

from .record import SpecRecord
from .loader import Loader
from .util import nofail

__all__ = "Finder",


class Finder(MetaPathFinder):
    LoaderType: type[Loader] = Loader
    SpecRecordType: type[SpecRecord] = SpecRecord

    def on_import(self, spec_record: SpecRecord):
        pass

    def on_preload(self, spec_record: SpecRecord):
        pass

    def on_load(self, spec_record: SpecRecord, stack: tuple[SpecRecord, ...] | None = None):
        pass

    @classmethod
    def install(cls, *, force: bool = False) -> Finder | None:
        if not force and any(isinstance(finder, cls) for finder in sys.meta_path):
            return None
        sys.meta_path.insert(0, self := cls())
        return self

    def __spec__(self, fullname, path=None, target=None) -> ModuleSpec | None:
        meta_path = False

        try:
            sys.meta_path.remove(self)
            meta_path = True
        except ValueError:
            pass

        try:
            return find_spec(fullname)

        finally:
            if meta_path:
                sys.meta_path.insert(0, self)

    def find_spec(self, fullname, path=None, target=None) -> ModuleSpec | None:
        record = self.SpecRecordType.register(
            finder=self,
            name=fullname,
            path=path,
            target=target,
        )
        nofail(self.on_import, record)
        return record.spec

    def invalidate_caches(self) -> None:
        self.SpecRecordType.RECORD.clear()
