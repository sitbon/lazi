from types import ModuleType
from contextlib import contextmanager
import importlib.util

from .record import SpecRecord
from .util import nofail

__all__ = "Loader",

# noinspection PyUnresolvedReferences,PyProtectedMember
_LazyModule: type[ModuleType] = importlib.util._LazyModule


class Loader(importlib.util.LazyLoader):
    spec_record: SpecRecord
    __stack__: list[SpecRecord] = []

    def __init__(self, spec_record: SpecRecord):
        self.spec_record = spec_record
        super().__init__(spec_record.spec.loader)

    @property
    def loaded(self) -> bool:
        return self.spec_record.used

    @property
    def stack(self) -> tuple[SpecRecord, ...]:
        return tuple(self.__stack__)

    def hook(self):
        assert self.spec_record.hook
        self.spec_record.spec.loader = self

    def on_preload(self):
        nofail(self.spec_record.on_preload)
        self.__stack__.append(self.spec_record)

    def on_load(self, stack: tuple[SpecRecord, ...]):
        assert not self.loaded
        assert self.__stack__.pop() is self.spec_record
        nofail(self.spec_record.on_load, stack)

    def exec_module(self, module):
        super().exec_module(module)

        # noinspection PyMethodParameters
        class LazyModule(_LazyModule):
            def __getattribute__(self_, attr):
                assert not self.loaded

                if attr == "__spec__":
                    return self.spec_record.spec

                with self.__load_context__():
                    return _LazyModule.__getattribute__(self_, attr)

            def __delattr__(self_, attr):
                return _LazyModule.__delattr__(self_,  attr)

        module.__class__ = LazyModule

    @contextmanager
    def __load_context__(self):
        self.on_preload()

        try:
            yield
        finally:
            self.on_load(self.stack)
