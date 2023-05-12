import lazi.auto
from lazi.core import *


def test_record_gen():
    django = lazy("django")
    django_test = lazy("django.test")
    TestCase = django_test.TestCase
    assert list(used())
