from lazi.core import lazi


def test_finder_lazy():

    django = lazi.lazy("django")
    version = django.VERSION
    test = lazi.lazy("django.test")
    TestCase = test.TestCase
