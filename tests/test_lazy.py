

def test_finder_lazy():
    from lazi.core import lazi

    with lazi:
        django = lazi.lazy("django")
        version = django.VERSION
        test = lazi.lazy("django.test")
        TestCase = test.TestCase

    del lazi
