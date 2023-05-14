import sys
import pytest
import _lazi


@pytest.mark.skipif(
    "not config.getoption('--standalone')",
    reason="Only run when --standalone is given",
)
@_lazi.param
def test_standalone(use_lazi):
    if use_lazi is not False:
        return _lazi.test(use_lazi, test_standalone)

    lazi = _lazi.core()

    with lazi.context():
        from standalone import sa_presto
        sys.modules.pop(sa_presto.__name__.split(".", 1)[0])
