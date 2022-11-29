from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "localdb.sqlite3",
    }
}

DEBUG = True

USE_BASIC_AUTH = False

SECRET_KEY = "secret-key"
