from lazi.core import *
from lazi.core import conf, __all__  # noqa

if not conf.CORE_AUTO_INSTALL and conf.LAZI_AUTO_INSTALL and not __finder__.__refs__:
    install()
