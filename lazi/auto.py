from lazi.conf import conf
from lazi.core import *
from lazi.core import __all__  # noqa

if not conf.CORE_AUTO_INSTALL and conf.LAZI_AUTO_INSTALL and not __finder__.__refs__:
    Finder.install()
