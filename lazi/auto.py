from lazi.core import *
from lazi.core import conf, __all__  # noqa

if not conf.CORE_AUTO_INSTALL and conf.LAZI_AUTO_INSTALL and not lazi.__refs__:
    lazi.__enter__()
