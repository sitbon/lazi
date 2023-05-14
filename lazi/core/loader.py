import sys
from types import ModuleType
from importlib.util import LazyLoader
from importlib.abc import Loader as _Loader
# noinspection PyUnresolvedReferences,PyProtectedMember
from importlib.util import _LazyModule  # type: type[ModuleType]

from lazi.conf import conf
from lazi.util import debug
from .record import SpecRecord

__all__ = "Loader",


class Loader(LazyLoader):
    spec_record: SpecRecord
    loader: _Loader  # set by LazyLoader

    def __init__(self, spec_record: SpecRecord):
        self.spec_record = spec_record
        super().__init__(spec_record.spec.loader)

    @property
    def used(self) -> bool:
        return self.spec_record.used

    def hook(self):
        assert self.spec_record.hook is True
        self.spec_record.spec.loader = self

    def pre_load(self):
        self.spec_record.pre_load()

    def on_load(self):
        self.spec_record.on_load()

    def on_load_exc(self, attr, exc):
        return self.spec_record.on_load_exc(attr, exc)

    def on_exec(self, module: ModuleType):
        return self.spec_record.on_exec(module)

    def post_exec(self, module: ModuleType | None) -> bool:
        return self.spec_record.post_exec(module)

    def exec_module(self, module: ModuleType):
        assert self.spec_record.spec is not None
        assert not self.used

        self.on_exec(module)

        # if self.post_exec(None) and conf.LOADER_AUTO_DEPS:
        #     # TODO(?): Early bypass here instead of constructing a LazyModule only to throw it away.
        #     assert None is debug.trace("exec_module", self.spec_record.name, "<force-early>")
        #     module.__spec__.loader = self.loader
        #     module.__loader__ = self.loader
        #     # ... ?
        #     return

        mdic = object.__getattribute__(module, "__dict__")

        super().exec_module(module)

        self.spec_record.spec.loader = self
        mdic["__loader__"] = self

        # noinspection PyMethodParameters
        class LazyModule(_LazyModule):
            def __setattr__(_, key, value):
                assert None is debug.trace("setattribute", self.spec_record.name, key)
                return super().__setattr__(key, value)

            def __getattribute__(_, attr):
                if attr == "__class__" or attr in conf.LOADER_FAKE_ATTR:
                    if attr in mdic:
                        return mdic[attr]

                    assert None is debug.trace("geeattribute", self.spec_record.name, attr)
                    raise AttributeError(attr)

                self.pre_load()

                self.spec_record.spec.loader = self.loader
                mdic["__loader__"] = self.loader

                try:
                    assert None is debug.trace("getattribute", self.spec_record.name, attr, "<load>")
                    valu = _LazyModule.__getattribute__(_, attr)

                except (ImportError, AttributeError, NameError) as exc:
                    # NOTE: This is currently untested, but something is still wrong with recursive/circular loading.
                    self.on_load_exc(attr, exc)
                    raise

                except Exception as exc:
                    self.on_load_exc(attr, exc)
                    raise AttributeError(attr) from exc

                else:
                    self.on_load()
                    return valu

                finally:
                    if mdic.get("__class__", LazyModule) is LazyModule:
                        self.spec_record.spec.loader = self
                        mdic["__loader__"] = self

            def __delattr__(_, attr):
                return _LazyModule.__delattr__(_,  attr)

        module.__class__ = LazyModule

        if self.post_exec(module) and conf.LOADER_AUTO_DEPS:
            # Bypass lazy loading in recursive situations (called here indirectly between pre_load and on_load).
            assert None is debug.trace("exec_module", self.spec_record.name, "<force>")
            # return self.spec_record.loader.exec_module(module)
            getattr(module, "__dict__", None)  # Force the module to load.
