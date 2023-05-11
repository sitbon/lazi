from types import ModuleType
from importlib.util import LazyLoader
# noinspection PyUnresolvedReferences,PyProtectedMember
from importlib.util import _LazyModule  # type: type[ModuleType]

from lazi.conf import conf
from .record import SpecRecord
from .util import trace

__all__ = "Loader",


class Loader(LazyLoader):
    spec_record: SpecRecord

    def __init__(self, spec_record: SpecRecord):
        self.spec_record = spec_record
        super().__init__(spec_record.spec.loader)

    @property
    def loaded(self) -> bool:
        return self.spec_record.used

    def hook(self):
        assert self.spec_record.hook is True
        self.spec_record.spec.loader = self

    def pre_load(self):
        return self.spec_record.pre_load()

    def on_load(self):
        assert self.loaded is False

        if conf.LOADER_AUTO_DEPS:
            for dep in (dep for dep in self.spec_record.deps if dep.spec is not None):
                # New discovery from this: dep.spec.loader gets changed between its on_create() and here.

                trace("dep_load", self.spec_record.name, "->", dep.spec, dep.loader, dep.spec.loader)

                getattr(dep.module, "__path__", None)  # Force the module to load.

        return self.spec_record.on_load()

    def on_create(self, module: ModuleType):
        return self.spec_record.on_create(module)

    def exec_module(self, module: ModuleType):
        self.on_create(module)
        super().exec_module(module)

        # noinspection PyMethodParameters
        class LazyModule(_LazyModule):
            def __getattribute__(self_, attr):
                trace("getattribute", self.spec_record.name, attr)

                assert self.loaded is False

                if attr in conf.LOADER_FAKE_ATTR:
                    match attr:
                        case "__spec__":
                            return self.spec_record.spec
                        case "__loader__":
                            return self
                        case "__name__":
                            return self.spec_record.name

                self.pre_load()

                try:
                    trace("getattribute", self.spec_record.name, attr, "load")
                    return _LazyModule.__getattribute__(self_, attr)  # Errors here are from the import two lines above (in trace)

                except Exception:
                    raise

                finally:
                    self.on_load()

            def __delattr__(self_, attr):
                return _LazyModule.__delattr__(self_,  attr)

        module.__class__ = LazyModule
