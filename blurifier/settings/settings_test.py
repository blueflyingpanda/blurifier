from fakeredis import FakeConnection

from blurifier.settings.settings import *  # noqa: F403

from threading import Thread
from fakeredis import TcpFakeServer

# Override the Redis cache backend with a fake one for testing purposes
server_address = (
    '127.0.0.1',
    6380,
)  # Use a different port to avoid conflicts with any real Redis server
server = TcpFakeServer(server_address, server_type='redis')
t = Thread(target=server.serve_forever, daemon=True)
t.start()

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6380/1',
        'OPTIONS': {'connection_class': FakeConnection},
    }
}

CELERY_TASK_ALWAYS_EAGER = (
    True  # execute synchronously in the same process instead of being sent to a worker
)
CELERY_TASK_EAGER_PROPAGATES = True  # makes task exceptions propagate up to your calling code instead of being stored in the result
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'  # instead of redis, use memory for results

DEBUG = False

try:
    INSTALLED_APPS.remove('debug_toolbar')  # noqa: F405
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405
except ValueError:
    pass  # debug_toolbar not in list

# Disable logging during tests to reduce noise
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}
