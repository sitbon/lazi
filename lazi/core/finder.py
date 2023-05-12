from __future__ import annotations

import sys
from types import ModuleType
from importlib.util import find_spec
from importlib.machinery import ModuleSpec
from importlib.abc import MetaPathFinder
from contextlib import contextmanager

from lazi.conf import conf
from lazi.util import Singleton, debug
from .record import SpecRecord
from .loader import Loader

__all__ = "Finder",


class Finder(Singleton, MetaPathFinder):
    LoaderType: type[Loader] = Loader
    SpecRecordType: type[SpecRecord] = SpecRecord
    __count__: int = 0
    __skip__: int = 0

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
        if self.__skip__:
            return None

        if not self.__count__:
            return None

        if conf.DEBUG_TRACING > 1:
            debug.trace(f"find_spec {fullname!r} {path!r} {target!r}")

        record = self.SpecRecordType.register(finder=self, name=fullname, path=path, target=target)

        return record.spec

    def import_spec(self, record: SpecRecord) -> ModuleSpec | None:
        """
        Import a module spec, if possible. Triggers recursive lazy loading.

        This is normally only called via SpecRecord.register() when a new record is created.

        TODO: Determine if passing package to find_spec would help. If so, where from?
        """
        self.__skip__ += 1

        try:
            return find_spec(record.name)

        finally:
            self.__skip__ -= 1

    def invalidate_caches(self) -> None:
        self.SpecRecordType.RECORD.clear()

    def pre_import(self, spec_record: SpecRecord) -> None:
        if conf.DEBUG_TRACING > 2:
            debug.trace("pre_import", spec_record.name, spec_record.spec)

    def on_import(self, spec_record: SpecRecord) -> None:
        if spec_record.hook or conf.DEBUG_TRACING > 1:
            if conf.DEBUG_TRACING > 2:
                debug.trace("on_import", spec_record.name, spec_record.path, spec_record.spec)
            else:
                debug.trace("on_import", spec_record.name, len(spec_record.path or []), int(spec_record.target or 0))

    def pre_load(self, spec_record: SpecRecord) -> None:
        debug.trace(
            "pre_load",
            f"{'+' if spec_record.used else '-'}{spec_record.name}",
            "<-",
            f"{'+' if spec_record.parent.used else '-'}{spec_record.parent.name}"
            if spec_record.parent else None,
            f"[{'/'.join(('-', '+')[int(sr.used)] + sr.name for sr in spec_record.__stack__)}]"
        )

    def on_load(self, spec_record: SpecRecord) -> None:
        debug.trace(
            "on_load",
            f"{'+' if spec_record.used else '-'}{spec_record.name}",
            "<-",
            f"{'+' if spec_record.parent.used else '-'}{spec_record.parent.name}" if spec_record.parent else None,
            f"[{'/'.join(('-', '+')[int(sr.used)] + sr.name for sr in spec_record.__stack__)}]"
        )

    def on_load_exc(self, spec_record: SpecRecord, attr: str, exc: Exception) -> None:
        if not isinstance(exc, AttributeError):
            debug.trace("on_load_exc", spec_record.name, attr, type(exc).__name__)

    def on_exec(self, spec_record: SpecRecord, module: ModuleType) -> None:
        debug.trace(
            "on_exec",
            f"{'+' if spec_record.used else '-'}{spec_record.name}",
            "<-",
            f"{'+' if spec_record.parent.used else '-'}{spec_record.parent.name}" if spec_record.parent else None,
            f"[{'/'.join(('-', '+')[int(sr.used)] + sr.name for sr in spec_record.__stack__)}]"
        )
