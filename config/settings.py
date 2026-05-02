import os
import sys
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def in_exe():
    return getattr(sys, "frozen", False)


if in_exe():
    EXE_DIR = Path(sys.executable).resolve().parent
else:
    EXE_DIR = BASE_DIR


def get_sqlite_db_path():
    configured_path = os.environ.get("SQLITE_DB_PATH")
    if configured_path:
        return Path(configured_path).expanduser().resolve()

    if not in_exe():
        return BASE_DIR / "db.sqlite3"

    candidates = [
        EXE_DIR.parent / "db.sqlite3",
        EXE_DIR / "db.sqlite3",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return EXE_DIR / "db.sqlite3"

SECRET_KEY = config('SECRET_KEY', default='django-insecure-temporary-secret-key-change-in-production')
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "samoschool.fly.dev", '*']

INSTALLED_APPS = [
    "dal",
    "dal_select2",
    "django_select2",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "rest_framework",
    "apps.accounts",
    "apps.students",
    "apps.payments",
    "apps.reports",
    "apps.printers",
    "apps.dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.accounts.middleware.AutoLoginMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"

DATABASE_URL = os.environ.get("DATABASE_URL")
DESKTOP_SQLITE = os.environ.get("DESKTOP_SQLITE", "1") == "1"



import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"

if in_exe():
    STATIC_ROOT = EXE_DIR / "staticfiles"
    STATICFILES_DIRS = []
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    STATIC_URL = "/static/"
    STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = EXE_DIR / "media" if in_exe() else BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
}

LOGIN_URL = "/dashboard/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/dashboard/"

RECEIPT_PREFIX = "RCPT"
