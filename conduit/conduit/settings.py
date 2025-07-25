# import os
# from datetime import timedelta
# from pathlib import Path
#
# import environ
#
# # Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
# ROOT_DIR = BASE_DIR.parent
#
# # read env var
# env = environ.Env()
# environ.Env.read_env(env_file=str(ROOT_DIR) + "/.env")
#
# # Quick-start development settings - unsuitable for production
# # See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/
#
# # SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = env("SECRET_KEY")
# # SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
#
# ALLOWED_HOSTS = ["*"]
# CSRF_TRUSTED_ORIGINS = ["http://localhost:5173", "http://localhost:5173"]
# CORS_ORIGIN_ALLOW_ALL = False
# CORS_ORIGIN_WHITELIST = ("http://localhost:5173", "http://localhost:5173")
# CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOW_HEADERS = (
#     "Origin",
#     "X-Requested-With",
#     "Content-Type",
#     "Accept",
#     "authorization",
#     "X-CSRFToken",
#     "x-csrftoken",
#     "X-CSRFTOKEN",
# )
#
#
# # Application definition
#
# INSTALLED_APPS = [
#     "django.contrib.admin",
#     "django.contrib.auth",
#     "django.contrib.contenttypes",
#     "django.contrib.sessions",
#     "django.contrib.messages",
#     "django.contrib.staticfiles",
#     # local apps
#     "users",
#     "abstract",
#     "storage",
#     "share",
#     "file_tree",
#     "notifications",
#     # third-party
#     "corsheaders",
#     "rest_framework",
#     "rest_framework_simplejwt.token_blacklist",
# ]
#
# MIDDLEWARE = [
#     "django.middleware.security.SecurityMiddleware",
#     "django.contrib.sessions.middleware.SessionMiddleware",
#     "corsheaders.middleware.CorsMiddleware",
#     "django.middleware.common.CommonMiddleware",
#     "django.middleware.csrf.CsrfViewMiddleware",
#     "django.contrib.auth.middleware.AuthenticationMiddleware",
#     "django.contrib.messages.middleware.MessageMiddleware",
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# ]
#
# ROOT_URLCONF = "conduit.urls"
#
# TEMPLATES = [
#     {
#         "BACKEND": "django.template.backends.django.DjangoTemplates",
#         "DIRS": [],
#         "APP_DIRS": True,
#         "OPTIONS": {
#             "context_processors": [
#                 "django.template.context_processors.debug",
#                 "django.template.context_processors.request",
#                 "django.contrib.auth.context_processors.auth",
#                 "django.contrib.messages.context_processors.messages",
#             ],
#         },
#     },
# ]
#
# WSGI_APPLICATION = "conduit.wsgi.application"
#
#
# # Database
# # https://docs.djangoproject.com/en/5.0/ref/settings/#databases
#
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": env("DB_NAME"),
#         "USER": env("DB_USER"),
#         "PASSWORD": env("DB_PASSWORD"),
#         "HOST": env("DB_HOST"),
#         "PORT": env("DB_PORT"),
#     }
# }
#
# AUTH_USER_MODEL = "users.User"
#
# # Password validation
# # https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
#
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
#     },
#     {
#         "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
#     },
#     {
#         "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
#     },
#     {
#         "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
#     },
# ]
#
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.redis.RedisCache",
#         "LOCATION": "redis://redis:6379",
#     }
# }
#
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "verbose": {
#             "format": "{levelname} {asctime} {module} {message}",
#             "style": "{",
#         },
#         "simple": {
#             "format": "{levelname} {message}",
#             "style": "{",
#         },
#     },
#     "handlers": {
#         "file": {
#             "level": "ERROR",
#             "class": "logging.FileHandler",
#             "filename": os.path.join(BASE_DIR, "debug.log"),
#             "formatter": "verbose",
#         },
#         "console": {
#             "level": "INFO",
#             "class": "logging.StreamHandler",
#             "formatter": "simple",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["file", "console"],
#             "level": "INFO",
#             "propagate": True,
#         },
#         "users": {
#             "handlers": ["file", "console"],
#             "level": "INFO",
#             "propagate": True,
#         },
#         "abstract": {
#             "handlers": ["file", "console"],
#             "level": "INFO",
#             "propagate": True,
#         },
#     },
# }
#
# # Email
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_HOST_USER = env("EMAIL_ADDRESS")
# EMAIL_HOST_PASSWORD = env("EMAIL_APP_PASSWORD")
# EMAIL_PORT = env("SMTP_PORT")
# EMAIL_USE_SSL = True
# DEFAULT_FROM_EMAIL = "conduit-app@gmail.com"
#
# # Internationalization
# # https://docs.djangoproject.com/en/5.0/topics/i18n/
#
# LANGUAGE_CODE = "en-us"
#
# TIME_ZONE = "UTC"
#
# USE_I18N = True
#
# USE_TZ = True
#
# AUTHENTICATION_BACKENDS = ["users.backends.EmailTagAuthenticationBackend"]
#
# # Static files (CSS, JavaScript, Images)
# # https://docs.djangoproject.com/en/5.0/howto/static-files/
#
# STATIC_URL = "static/"
#
# # Default primary key field type
# # https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
#
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
#
# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": (
#         "users.authenticate.JWTTokenCookieAuthentication",
#     )
# }
#
# SIMPLE_JWT = {
#     "USER_ID_FIELD": "uid",
#     "ACCESS_TOKEN_LIFETIME": timedelta(hours=5),
#     "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
#     # cookies
#     "AUTH_COOKIE": "access_token",  # Cookie name. Enables cookies if value is set.
#     "AUTH_COOKIE_DOMAIN": None,  # A string like "example.com", or None for standard domain cookie.
#     "AUTH_COOKIE_SECURE": False,  # Whether the auth cookies should be secure (https:// only).
#     "AUTH_COOKIE_HTTP_ONLY": True,  # Http only cookie flag.It's not fetch by javascript.
#     "AUTH_COOKIE_PATH": "/",  # The path of the auth cookie.
#     "AUTH_COOKIE_SAMESITE": "Lax",  # Whether to set the flag restricting cookie leaks on cross-site requests. This can be 'Lax', 'Strict', or None to disable the flag.
# }
#
#
# CELERY_TIMEZONE = "UTC"
# # CELERY_BROKER_URL = "redis://localhost:6379"
# # CELERY_RESULT_BACKEND = "redis://localhost:6379"
#
# CELERY_BROKER_URL = env("CELERY_BROKER_URL")
# CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
#
# GITHUB_OAUTH_CLIENT_ID = env("GITHUB_OAUTH_CLIENT_ID")
# GITHUB_OAUTH_CLIENT_SECRET = env("GITHUB_OAUTH_CLIENT_SECRET")
# GITHUB_OAUTH_CALLBACK_URL = "http://localhost:8000/api/v1/users/oauth/github/callback/"
