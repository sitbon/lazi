from django.apps import AppConfig


class TestDjangoAppConfig(AppConfig):
    name = 'tests.test_django.web'
    label = 'web'
    verbose_name = 'tests.test_django.web'
    default_auto_field = 'django.db.models.BigAutoField'
