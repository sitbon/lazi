import os
import urllib.parse
from pathlib import Path

DEBUG = True

PROJECT_DIR = Path(__file__).parent
BASE_DIR = PROJECT_DIR

SECRET_KEY = "secret"

INSTALLED_APPS = [
    "wagtail",
    "wagtail.sites",
    "wagtail.users",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",

    "tests.test_django.web",
]


MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
]

ROOT_URLCONF = "web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "tests.test_django.web.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "data", "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "US/Pacific"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# JavaScript / CSS assets being served from cache (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/4.1/ref/contrib/staticfiles/#manifeststaticfilesstorage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django.contrib.staticfiles.finders.FileSystemFinder",
]

STATIC_ROOT = os.path.join(BASE_DIR, "data", "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "data", "media")
MEDIA_URL = "/media/"


STATICFILES_DIRS = [
    # os.path.join(PROJECT_DIR, "static"),
]

# Django login/logout settings.
LOGIN_URL = "/admin/login/"

LOGIN_REDIRECT_URL = "/admin/"

LOGOUT_REDIRECT_URL = "/"

# Django REST Framework settings

# REST_FRAMEWORK = {
#     "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
#     "PAGE_SIZE": 100,
#     "DEFAULT_AUTHENTICATION_CLASSES": (
#         "rest_framework.authentication.SessionAuthentication",
#         "rest_framework.authentication.BasicAuthentication",
#         "web.base.api.auth.TokenAuthentication",
#     ),
# }
#
# REST_KNOX = {
#     "SECURE_HASH_ALGORITHM": "cryptography.hazmat.primitives.hashes.SHA512",
#     "AUTH_TOKEN_CHARACTER_LENGTH": 64,
#     "TOKEN_TTL": timedelta(days=7),
#     "USER_SERIALIZER": "knox.serializers.UserSerializer",
#     "TOKEN_LIMIT_PER_USER": None,
#     "MIN_REFRESH_INTERVAL": 10,
#     "AUTO_REFRESH": True,
# }

# Wagtail settings

WAGTAIL_SITE_NAME = "web"

# # Search
# # https://docs.wagtail.org/en/stable/topics/search/backends.html
# WAGTAILSEARCH_BACKENDS = {
#     "default": {
#         "BACKEND": "wagtail.search.backends.database",
#     }
# }
#
# # For wagtail.images
# #
# WAGTAILIMAGES_IMAGE_MODEL = "site.SiteImage"
#
# # For wagtail.documents
# #
#
# WAGTAILDOCS_DOCUMENT_MODEL = "site.SiteDocument"
#
# # For wagtailmedia
# #
# WAGTAILMEDIA = {
#     "MEDIA_MODEL": "site.SiteMedia",
#     "MEDIA_FORM_BASE": "",
#     # "AUDIO_EXTENSIONS": [],
#     # "VIDEO_EXTENSIONS": [],
# }
#
# # From https://github.com/spapas/wagtail-faq
# WAGTAILDOCS_SERVE_METHOD = "serve_view"
# SENDFILE_BACKEND = "web.util.sendfile"
# SENDFILE_ROOT = os.path.join(MEDIA_ROOT, "documents")
# SENDFILE_URL = urllib.parse.urljoin(MEDIA_URL, "documents")

# For nginx CSRF compatibility
#
SECURE_PROXY_SSL_HEADER = ("X-Forwarded-Proto", "https")
#
