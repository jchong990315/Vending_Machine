# we need this to avoid running our db during test for admins
from .settings import * # noqa: F403,F401

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }
}
# disables unncessary logins
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# allow test client’s default host
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
