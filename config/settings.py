import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent


# =====================
# CORE
# =====================
SECRET_KEY = config("SECRET_KEY", default="django-insecure-temp-key")
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "samoschoolpayment.up.railway.app",
]


# =====================
# APPS
# =====================
INSTALLED_APPS = [
    "dal",
    "dal_select2",
    "django_select2",

    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    "rest_framework",

    "apps.students",
    "apps.payments",
    "apps.reports",
    "apps.printers",
    "apps.dashboard",
]


# =====================
# MIDDLEWARE (LOGIN YO‘Q)
# =====================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


# =====================
# TEMPLATES
# =====================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# =====================
# DATABASE
# =====================
import os
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get("DATABASE_URL")
    )
}


# =====================
# I18N
# =====================
LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True


# =====================
# STATIC
# =====================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =====================
# DEFAULT FIELD
# =====================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =====================
# REST
# =====================
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}


# =====================
# CUSTOM
# =====================
RECEIPT_PREFIX = "RCPT"