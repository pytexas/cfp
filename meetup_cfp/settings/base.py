"""
Base settings for the meetup_cfp project.

Environment-specific settings (``dev``, ``prod``) import from this module and
override as needed. The active module is chosen via ``DJANGO_SETTINGS_MODULE``
(defaults to ``meetup_cfp.settings.dev`` — see ``manage.py`` / ``wsgi.py``).

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

from pathlib import Path

# Repository root: settings/ -> meetup_cfp/ -> project root.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = "django-insecure-d@ahvp!v!k*l-aa2z2khscz+qortey=sg7u@y-n8i8_9woaynw"

DEBUG = False

ALLOWED_HOSTS: list[str] = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "django_tailwind_cli",
    "django_htmx",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "meetup_cfp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "meetup_cfp.context_processors.navigation",
            ],
        },
    },
]

WSGI_APPLICATION = "meetup_cfp.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

# UTC storage; single org-wide display timezone (see spec.md).
TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "assets"]


# django-tailwind-cli (Tailwind CSS 4.x, bundled standalone CLI — no Node.js)
# https://django-tailwind-cli.rtfd.io/
TAILWIND_CLI_SRC_CSS = "assets/css/source.css"
TAILWIND_CLI_DIST_CSS = "css/tailwind.css"
TAILWIND_CLI_VERSION = "4.1.3"
# Use a local copy of the standalone CLI at .tailwind/tailwindcss (git-ignored).
# See README for the one-line curl to fetch it; the built-in auto-downloader
# needs system CA certs that this Python build is missing.
TAILWIND_CLI_PATH = str(BASE_DIR / ".tailwind" / "tailwindcss")
TAILWIND_CLI_AUTOMATIC_DOWNLOAD = False


# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
