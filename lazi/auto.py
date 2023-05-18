from lazi.core import *
from lazi.core import conf, __all__  # noqa

if not conf.CORE_AUTO and conf.AUTO_AUTO and not lazi.refs:
    lazi.__enter__()
