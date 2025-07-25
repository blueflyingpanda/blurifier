from .settings import *

DATABASES['default'] = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "blurifier_test",
    "USER": "blurifier_test",
    "PASSWORD": "test",
    "HOST": "localhost",
    "PORT": "5432",
}
