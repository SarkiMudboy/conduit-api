import os

from dotenv import load_dotenv

from .base import *  # noqa

# read env var
load_dotenv(".env.local")

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", True)

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS").split(",")
CORS_ORIGIN_ALLOW_ALL = False
CORS_ORIGIN_WHITELIST = ("http://localhost:5173", "http://localhost:5173")
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (
    "Origin",
    "X-Requested-With",
    "Content-Type",
    "Accept",
    "authorization",
    "X-CSRFToken",
    "x-csrftoken",
    "X-CSRFTOKEN",
)

# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "debug.log"),  # noqa
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "users": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "abstract": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = os.getenv("EMAIL_ADDRESS")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_PORT = os.getenv("SMTP_PORT")
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = "conduit-app@gmail.com"


CELERY_TIMEZONE = "UTC"
# CELERY_BROKER_URL = "redis://localhost:6379"
# CELERY_RESULT_BACKEND = "redis://localhost:6379"

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

GITHUB_OAUTH_CLIENT_ID = os.getenv("GITHUB_OAUTH_CLIENT_ID")
GITHUB_OAUTH_CLIENT_SECRET = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")
GITHUB_OAUTH_CALLBACK_URL = "http://localhost:8000/api/v1/users/oauth/github/callback/"
