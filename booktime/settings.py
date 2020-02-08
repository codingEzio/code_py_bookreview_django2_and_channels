import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # mine
    "main.apps.MainConfig",
    # dev
    "django_extensions",
    "debug_toolbar",
    # prod
    "webpack_loader",
    "django_tables2",
    "widget_tweaks",  # tweak the form field rendering in templates
    "rest_framework",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "main.middlewares.basket_middleware",
]

ROOT_URLCONF = "booktime.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "booktime.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# Steps:
# ~1 createuser -dP USER
# ~2 createdb   -E utf-8 -U USER DATABASE
# ~3 psql --username=USER --dbname=DATABASE
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRESQL_DB_NAME"),
        "USER": os.getenv("POSTGRESQL_USER"),
        "PASSWORD": os.getenv("POSTGRESQL_PASSWORD"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

PASSWD_VALI_PREFIX = "django.contrib.auth.password_validation."
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"{PASSWD_VALI_PREFIX}UserAttributeSimilarityValidator"},
    {"NAME": f"{PASSWD_VALI_PREFIX}MinimumLengthValidator"},
    {"NAME": f"{PASSWD_VALI_PREFIX}CommonPasswordValidator"},
    {"NAME": f"{PASSWD_VALI_PREFIX}NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

USE_I18N = True
USE_L10N = True

TIME_ZONE = "UTC"
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"

# Site-related (e.g. JS, CSS) (You don't need to touch the 1st one while dev)
STATIC_ROOT = os.path.join(BASE_DIR, "staticdeploy/")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "staticdev/")]

# User-uploaded
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")


# Email

EMAIL_BACKEND = os.getenv("CURRENT_EMAIL_BACKEND")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")


# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(levelname)s %(message)s"},},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        # app
        "main": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
        # project
        "booktime": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


# Custom user model (use email only instead of username)

# Use our own version of `User` model
AUTH_USER_MODEL = "main.User"


# LoginView settings

LOGIN_REDIRECT_URL = "/"


# Third-party library - django-debug-toolbar


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar,
}


# Third-party library - django-webpack-loader

WEBPACK_LOADER = {
    "DEFAULT": {
        "BUNDLE_DIR_NAME": "bundles/",
        "STATS_FILE": os.path.join(BASE_DIR, "webpack-stats.json"),
    }
}


# Third-party library - django-tables2

# Specify what templates to use when rendering tables
#  https://django-tables2.readthedocs.io/en/latest/pages/custom-rendering.html
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap.html"


# Third-party library - django-tables2

# fmt: off
REST = "rest_framework"
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        f"{REST}.authentication.SessionAuthentication",
        f"{REST}.authentication.BasicAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        f"{REST}.permissions.DjangoModelPermissions",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        f"django_filters.{REST}.DjangoFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": f"{REST}.pagination.PageNumberPagination",
    "PAGE_SIZE": 3,
}
