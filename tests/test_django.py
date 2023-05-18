

def test_django_version_lazy():
    from lazi.util import debug
    from lazi.core.finder import Finder

    with Finder() as finder:
        debug.trace("test_django_version_lazy: finder.lazy ->")
        django = finder.lazy("django")
        debug.trace("test_django_version_lazy: ^- finder.lazy")
        version = django.VERSION
        debug.trace(f"test_django_version_lazy: ^- VERSION: {version}")
        assert isinstance(version, tuple), version


def test_django_version_import():
    from lazi.util import debug
    from lazi.core.finder import Finder

    with Finder():
        debug.trace("test_django_version_import: import django ->")
        import django
        debug.trace("test_django_version_import: ^- import django")
        version = django.VERSION
        debug.trace(f"test_django_version_import: ^- VERSION: {version}")
        assert isinstance(version, tuple), version


def test_asgiref():
    from lazi.util import debug
    from lazi.core import lazi

    with lazi:
        debug.trace("-> from asgiref.sync import sync_to_async ->")
        from asgiref.sync import sync_to_async
        debug.trace("^- from asgiref.sync import sync_to_async -^")
