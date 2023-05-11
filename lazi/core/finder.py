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


# noinspection PyMethodMayBeStatic,PyPep8Naming
class Finder(MetaPathFinder):
    LoaderType: type[Loader] = Loader
    SpecRecordType: type[SpecRecord] = SpecRecord
    __finder__: Finder | None = None
    __count__: int = 0

    def __init__(self) -> None:
        assert self.__finder__ is None

    @classmethod
    def install(cls) -> Finder:
        if cls.__finder__ is not None:
            cls.__finder__.__count__ += 1
            return cls.__finder__

        sys.meta_path.insert(0, self := cls.__finder())
        self.__count__ += 1
        return self

    @classmethod
    def uninstall(cls) -> bool:
        assert cls.__finder__ is not None
        cls.__finder__.__count__ -= 1
        assert cls.__finder__.__count__ >= 0
        if cls.__finder__.__count__ == 0:
            sys.meta_path.remove(cls.__finder__)
            cls.__finder__.invalidate_caches()
            cls.__finder__ = None
            return True

    @classmethod
    def __finder(cls) -> Finder:
        if cls.__finder__ is None:
            cls.__finder__ = cls()
        return cls.__finder__

    @classmethod
    def Import(cls, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> ModuleType:
        return cls.__finder().import_module(name, path, target)

    @classmethod
    def ImportRecord(cls, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> SpecRecord:
        return cls.__finder().import_record(name, path, target)

    def import_module(self, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> ModuleType:
        record = self.import_record(name, path, target)
        if record.spec is None:
            raise ModuleNotFoundError(f"No module named {name!r}", name=name, path=path)
        return record.module

    def import_record(self, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> SpecRecord:
        return self.SpecRecordType.register(finder=self, name=name, path=path, target=target)

    def find_spec(self, fullname, path=None, target=None) -> ModuleSpec | None:
        return self.SpecRecordType.register(finder=self, name=fullname, path=path, target=target).spec

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

    def invalidate_caches(self) -> None:
        self.SpecRecordType.RECORD.clear()

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
