import os

from dotenv import load_dotenv

from .base import *  # noqa

load_dotenv(".env.prod")

DEBUG = os.getenv("DEBUG", False)

SECRET_KEY = os.getenv("SECRET_KEY")  # noqa
if not SECRET_KEY:
    raise ValueError("SECRET KEY must be set")

ALLOWED_HOSTS = []  # add this when ready!


SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# Session and CSRF Security
# SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS").split(",")

# Database Configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "postgres"),  # noqa
        "USER": os.getenv("DB_USER"),  # noqa
        "PASSWORD": os.getenv("DB_PASSWORD"),  # noqa
        "HOST": os.getenv("DB_HOST"),  # noqa
        "PORT": os.getenv("DB_PORT", "5432"),  # noqa
        "OPTIONS": {
            "sslmode": "require",
            "connect_timeout": 20,
        },
        "CONN_MAX_AGE": 300,  # Connection pooling
    }
}

# Cache Configuration (Redis on ElastiCache)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
        },
        "KEY_PREFIX": "django_cache",
        "TIMEOUT": 300,  # 5 minutes default
    }
}


# Celery Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
# CELERY_WORKER_PREFETCH_MULTIPLIER = 1
# CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Static Files Configuration
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # noqa

# Media Files Configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles")  # noqa


# if os.getenv("USE_S3") == "True":
#     AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
#     AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
#     AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
#     AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
#     AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
#     AWS_DEFAULT_ACL = "public-read"
#     AWS_S3_OBJECT_PARAMETERS = {
#         "CacheControl": "max-age=86400",
#     }


# setup email...
EMAIL_BACKEND = "django_ses.SESBackend"
AWS_SES_REGION_NAME = os.getenv("AWS_SES_REGION_NAME", "us-east-1")
AWS_SES_REGION_ENDPOINT = f"email.{AWS_SES_REGION_NAME}.amazonaws.com"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@conduit.com")
SERVER_EMAIL = DEFAULT_FROM_EMAIL


# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "json": {
            "format": '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/tmp/django.log",
            "maxBytes": 1024 * 1024 * 10,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "conduit": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


# Health Check Configuration
HEALTH_CHECK = {
    "DISK_USAGE_MAX": 90,  # percent
    "MEMORY_MIN": 100,  # in MB
}

# CORS Configuration (if you have a frontend)
if "corsheaders" in INSTALLED_APPS:  # noqa
    CORS_ALLOWED_ORIGINS = [
        "https://conduit.netlify.app",
        "https://conduit.netlify.app/",
    ]
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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "users.authenticate.JWTTokenCookieAuthentication",
    ),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "100/hour", "user": "1000/hour"},
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

BASE_APP_URL = os.getenv("BASE_APP_URL", "http://localhost:8000")

GITHUB_OAUTH_CLIENT_ID = os.getenv("GITHUB_OAUTH_CLIENT_ID")
GITHUB_OAUTH_CLIENT_SECRET = os.getenv("GITHUB_OAUTH_CLIENT_SECRET")
GITHUB_OAUTH_CALLBACK_URL = f"{BASE_APP_URL}/api/v1/users/oauth/github/callback/"
