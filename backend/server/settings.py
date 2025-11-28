# server/settings.py
import os
from pathlib import Path

# Optional: if you install dj-database-url, uncomment and use it
# import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# Core flags / secrets
# -------------------------------------------------------------------
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

# For dev, we allow a fallback; in prod we override this with a required env
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "dev-unsafe-secret-key-change-me",
)

SIGNUP_ACCESS_CODE = os.getenv("SIGNUP_ACCESS_CODE", "")

# -------------------------------------------------------------------
# Hosts / CORS / CSRF
# -------------------------------------------------------------------
# In dev, keep this broad. In prod we override ALLOWED_HOSTS.
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if os.getenv(
    "DJANGO_ALLOWED_HOSTS"
) else []

# Frontend origins (Quasar dev, plus whatever you add)
_default_cors = "http://localhost:9000,http://127.0.0.1:9000"
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ALLOWED_ORIGINS", _default_cors).split(",")
    if o.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.getenv("CSRF_TRUSTED_ORIGINS", _default_cors).split(",")
    if o.strip()
]

CORS_ALLOW_CREDENTIALS = True

# Cookie flags – relaxed for dev. In prod we override to Secure/None.
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CSRF_USE_SESSIONS = True

# -------------------------------------------------------------------
# Apps
# -------------------------------------------------------------------
INSTALLED_APPS = [
    "corsheaders",  # keep this before Django's common middleware
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",

    # Local apps
    "gym",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # add templates dirs if needed
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "server.wsgi.application"

# -------------------------------------------------------------------
# Database
# -------------------------------------------------------------------
# Strategy:
# - If DATABASE_URL env is set -> use that (Supabase, Railway, etc.)
# - Otherwise fall back to your local Postgres settings from dev
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    from urllib.parse import urlparse

    url = urlparse(DATABASE_URL)

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": url.path.lstrip("/"),
            "USER": url.username,
            "PASSWORD": url.password,
            "HOST": url.hostname,
            "PORT": str(url.port or ""),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "gymapp",
            "USER": "gymuser",
            "PASSWORD": "100Could!",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }

# -------------------------------------------------------------------
# Password validation
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
# I18N / TZ
# -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# Static / media
# -------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# You can add MEDIA_* later if you start using uploads.
# MEDIA_URL = "/media/"
# MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------------------------
# Logging (dev-friendly)
# -------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}