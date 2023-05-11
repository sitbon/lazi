from lazi.core import *

if not conf.CORE_AUTO_INSTALL and conf.LAZI_AUTO_INSTALL:
    Finder.install()
