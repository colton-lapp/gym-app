# server/settings_prod.py
import os
from .settings import *  # noqa

DEBUG = False

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
    if h.strip()
]

CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

CORS_ALLOW_CREDENTIALS = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SAMESITE = "None"

# Important: subdomain cookie so frontend + API share it
SESSION_COOKIE_DOMAIN = ".getswolemakegraphs.com"
CSRF_COOKIE_DOMAIN = ".getswolemakegraphs.com"

# Explicitly keep this OFF so frontend can read csrftoken
CSRF_COOKIE_HTTPONLY = False

# DO NOT set CSRF_USE_SESSIONS here
# CSRF_USE_SESSIONS = True  # leave commented/removed

LOGGING["root"]["level"] = "INFO"
LOGGING["loggers"]["django.request"]["level"] = "INFO"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["PGDATABASE"],
        "USER": os.environ["PGUSER"],
        "PASSWORD": os.environ["PGPASSWORD"],
        "HOST": os.environ["PGHOST"],
        "PORT": os.environ["PGPORT"],
    }
}