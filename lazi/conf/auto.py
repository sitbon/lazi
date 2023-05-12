import sys
from types import ModuleType

from lazi.util import SingletonMeta

from lazi.conf import conf

conf.clear()  # noqa: Clear the conf cache.
conf.get()  # noqa: Force the conf cache to reload.


class AutoConf(ModuleType, metaclass=SingletonMeta):
    def __init__(self):
        super().__init__(__name__)
        self.__getattr__ = lambda attr: getattr(conf, attr)

    def __call__(self):
        return self


sys.modules[__name__] = AutoConf()  # Be like conf from here (but keep this module intact).
