

def test_django_version_lazy():
    from lazi.core.hook.finder import Finder

    with Finder() as finder:
        django = finder.lazy("django")
        assert isinstance(django.VERSION, tuple), django.VERSION


def test_django_version_import():
    from lazi.core.hook.finder import Finder

    with Finder():
        import django
        assert isinstance(django.VERSION, tuple), django.VERSION
