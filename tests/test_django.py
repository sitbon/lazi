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
    print(lazi.used_count())
    TestCase = django.test.TestCase
    print(lazi.used_count())


def test_django_template_auto():
    import lazi.auto
    from django.template import Template
    print(lazi.used_count())
