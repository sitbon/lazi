"""Automatic lazy loading example.
"""


def test_django_test_auto():
    """
    dep_load[recursive-exc] django.template -> django.template.autoreload
    cannot import name 'DjangoTemplates' from 'django.template.backends.django'
    (/home/jq/.cache/pypoetry/virtualenvs/lazi-5AqQzycq-py3.11/lib/python3.11/site-packages/django/template/backends/django.py)
    """

    import lazi.auto
    import django.test
    TestCase = django.test.TestCase


def test_django_template_auto():
    import lazi.auto
    from django.template import Template


def test_django_math():
    import lazi.auto
    from django.db.models.functions import math


def test_django_db_agg():
    """Likely source of problems in above test."""
    import lazi.auto
    from django.db.models.aggregates import __all__


if __name__ == '__main__':
    test_django_db_agg()
