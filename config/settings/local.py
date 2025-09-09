"""Local project settings."""

from .base import *
from .base import env

from decouple import config


# General
# ------------------------------------------------------------------------------

DEBUG = True
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]
SECRET_KEY = env("DJANGO_SECRET_KEY", "shhh")

#  Databases
# ------------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT")
    },
}


# Email
# ------------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@littlenote.local"
SERVER_EMAIL = DEFAULT_FROM_EMAIL
