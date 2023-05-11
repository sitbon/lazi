from __future__ import annotations

import sys
from types import ModuleType
from importlib.util import find_spec
from importlib.machinery import ModuleSpec
from importlib.abc import MetaPathFinder

from .record import SpecRecord
from .loader import Loader
from .util import trace

__all__ = "Finder",


# noinspection PyMethodMayBeStatic
class Finder(MetaPathFinder):
    LoaderType: type[Loader] = Loader
    SpecRecordType: type[SpecRecord] = SpecRecord

    def pre_import(self, spec_record: SpecRecord) -> None:
        return  # trace("pre_import", spec_record.name, spec_record.spec)

    def on_import(self, spec_record: SpecRecord) -> None:
        return trace("on_import", spec_record.name, spec_record.spec)

    def pre_load(self, spec_record: SpecRecord) -> None:
        return trace("pre_load", spec_record.name, spec_record.spec)

    def on_load(self, spec_record: SpecRecord) -> None:
        return trace("on_load", spec_record.name, spec_record.spec)

    def on_create(self, spec_record: SpecRecord, module: ModuleType) -> None:
        return trace("on_create", spec_record.name, spec_record.spec, module)

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
        # trace("find_spec", fullname, path, target)
        record = self.SpecRecordType.register(
            finder=self,
            name=fullname,
            path=path,
            target=target,
        )
        return record.spec

    def invalidate_caches(self) -> None:
        self.SpecRecordType.RECORD.clear()
