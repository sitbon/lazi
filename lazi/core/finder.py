from __future__ import annotations

import sys
from types import ModuleType
from importlib.util import find_spec
from importlib.machinery import ModuleSpec
from importlib.abc import MetaPathFinder
from contextlib import contextmanager

from lazi.conf import conf
from lazi.util import Singleton, classproperty, debug
from .record import SpecRecord
from .loader import Loader

__all__ = "Finder",


class Finder(Singleton, MetaPathFinder):
    LoaderType: type[Loader] = Loader
    SpecRecordType: type[SpecRecord] = SpecRecord
    __refs__: int = 0
    __skip: int = 0

    instance = classproperty(lambda cls: cls.__instance__)
    refs = classproperty(lambda cls: cls.__instance__.__refs__)

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
        assert None is debug.trace(f"install {self.__class__.__name__}[{self.__refs__}]")

        if self not in sys.meta_path:
            sys.meta_path.insert(0, self)

        self.__refs__ += 1
        return self

    def __uninstall(self) -> Finder | None:
        assert None is debug.trace(f"uninstall {self.__class__.__name__}[{self.__refs__}]")

        if self.__refs__ == 0:
            return None

        assert self.__refs__ > 0
        assert self in sys.meta_path

        self.__refs__ -= 1

        if self.__refs__ == 0:
            sys.meta_path.remove(self)
            self.invalidate_caches()
            super().__delete__()
            return None

        return self

    @classmethod
    def lazy_module(cls, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> ModuleType:
        record = cls.lazy_record(name, path, target)
        if record.spec is None:
            raise ModuleNotFoundError(f"No module named {name!r}", name=name, path=path)
        return record.module

    @classmethod
    def lazy_record(cls, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> SpecRecord:
        return (self := cls.__instance__).SpecRecordType.find(finder=self, name=name, path=path, target=target)

    def find_spec(self, fullname, path=None, target=None) -> ModuleSpec | None:
        assert self.__skip >= 0
        if self.__skip:
            return None

        if conf.DEBUG_TRACING > 1:
            assert None is debug.trace(f"find_spec {fullname!r} {path!r} {target!r}")

        return self.SpecRecordType.find(finder=self, name=fullname, path=path, target=target).spec

    def import_spec(self, record: SpecRecord) -> ModuleSpec | None:
        """
        Import a module spec, if possible. Triggers recursive lazy loading.

        This is normally only called via SpecRecord.find() when a new record is created.
        """
        assert self.__skip >= 0
        self.__skip += 1
        try:
            return find_spec(record.name)
        finally:
            self.__skip -= 1

    def invalidate_caches(self) -> None:
        self.SpecRecordType.RECORD.clear()

    def pre_import(self, spec_record: SpecRecord) -> None:
        if conf.DEBUG_TRACING > 2:
            assert None is debug.trace("pre_import", spec_record.name, spec_record.spec)

    def on_import(self, spec_record: SpecRecord) -> None:
        if spec_record.hook or conf.DEBUG_TRACING > 1:
            if conf.DEBUG_TRACING > 2:
                assert None is debug.trace("on_import", spec_record.name, spec_record.path, spec_record.spec)
            else:
                assert None is debug.trace("on_import", spec_record.debug_repr)

    def pre_load(self, spec_record: SpecRecord) -> None:
        assert None is debug.trace("pre_load", spec_record.debug_repr)

    def on_load(self, spec_record: SpecRecord) -> None:
        assert None is debug.trace("on_load", spec_record.debug_repr)

    def on_load_exc(self, spec_record: SpecRecord, attr: str | None, exc: Exception) -> None:
        assert None is debug.trace("on_load_exc", spec_record.name, attr, type(exc).__name__, exc)
        assert None is debug.trace("           ", spec_record.debug_repr)

    def on_exec(self, spec_record: SpecRecord, module: ModuleType) -> None:
        assert None is debug.trace("on_exec", spec_record.debug_repr)

    def post_exec(self, spec_record: SpecRecord, module: ModuleType) -> bool | None:
        assert None is debug.trace("post_exec", spec_record.debug_repr)
        return
