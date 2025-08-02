"""Local project settings."""

from .base import *
from .base import env


# General
# ------------------------------------------------------------------------------

DEBUG = True
ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]
SECRET_KEY = env("DJANGO_SECRET_KEY", "shhh")
