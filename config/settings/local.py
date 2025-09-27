"""Local project settings."""

from .base import *

from decouple import config


# General
# ------------------------------------------------------------------------------

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
SECRET_KEY = config("DJANGO_SECRET_KEY", default="shhh")

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
