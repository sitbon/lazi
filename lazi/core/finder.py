from __future__ import annotations

import sys
from types import ModuleType
from importlib.util import find_spec
from importlib.machinery import ModuleSpec
from importlib.abc import MetaPathFinder
from contextlib import contextmanager

from lazi.util import Singleton, debug
from .record import SpecRecord
from .loader import Loader

__all__ = "Finder",


class Finder(Singleton, MetaPathFinder):
    LoaderType: type[Loader] = Loader
    SpecRecordType: type[SpecRecord] = SpecRecord
    __count__: int = 0
    __stack__: list[SpecRecord] = []

    @classmethod
    @contextmanager
    def context(cls) -> Finder:
        finder = cls.__instance__.__install()
        try:
            yield finder
        finally:
            cls.__instance__.__uninstall()

    @classmethod
    def install(cls) -> Finder:
        return cls.__instance__.__install()

    @classmethod
    def uninstall(cls) -> bool:
        return cls.__instance__.__uninstall()

    def __install(self) -> Finder:
        debug.trace(f"install {self.__class__.__name__}[{self.__count__}]")

        if self not in sys.meta_path:
            sys.meta_path.insert(0, self)

        self.__count__ += 1
        return self

    def __uninstall(self) -> bool:
        debug.trace(f"uninstall {self.__class__.__name__}[{self.__count__}]")

        assert self.__count__ > 0
        assert self in sys.meta_path

        self.__count__ -= 1

        if self.__count__ == 0:
            sys.meta_path.remove(self)
            self.invalidate_caches()
            self.__instance__ = None
            return True

        return False

    @classmethod
    def lazy_module(cls, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> ModuleType:
        record = cls.lazy_record(name, path, target)
        if record.spec is None:
            raise ModuleNotFoundError(f"No module named {name!r}", name=name, path=path)
        return record.module

    @classmethod
    def lazy_record(cls, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> SpecRecord:
        return (self := cls.__instance__).SpecRecordType.register(finder=self, name=name, path=path, target=target)

    def find_spec(self, fullname, path=None, target=None) -> ModuleSpec | None:
        return None if not self.__count__ else \
            self.SpecRecordType.register(finder=self, name=fullname, path=path, target=target).spec

    def import_spec(self, record: SpecRecord) -> ModuleSpec | None:
        """
        Import a module spec, if possible. Triggers recursive lazy loading.

        This is normally only called via SpecRecord.register() when a new record is created.

        TODO: Determine if passing package to find_spec would help. If so, where from?
        """
        if record in self.__stack__:
            return None

        self.__stack__.append(record)

        try:
            return find_spec(record.name)

        finally:
            pop = self.__stack__.pop()
            assert pop is record

    def invalidate_caches(self) -> None:
        self.SpecRecordType.RECORD.clear()

    def pre_import(self, spec_record: SpecRecord) -> None:
        return  # debug.trace("pre_import", spec_record.name, spec_record.spec)

    def on_import(self, spec_record: SpecRecord) -> None:
        return debug.trace("on_import", spec_record.name, spec_record.path, spec_record.spec)

    def pre_load(self, spec_record: SpecRecord) -> None:
        return debug.trace("pre_load", spec_record.name)

    def on_load(self, spec_record: SpecRecord, exc=None) -> None:
        return debug.trace("on_load", spec_record.name, exc)

    def on_create(self, spec_record: SpecRecord, module: ModuleType) -> None:
        return debug.trace("on_create", spec_record.name, module)
