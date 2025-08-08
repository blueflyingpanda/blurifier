import os
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic.types import SecretStr


# TODO: Grafana/Prometheus
# TODO: Elasticsearch/Logstash/Kibana
# TODO: Sentry
# TODO: graphQL
# TODO: Hugging Face/Langchain
# TODO: ai agents? mcp?
# TODO: protobuf/grpc api


class AppSettings(BaseSettings):
    # Database settings
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_pass: SecretStr

    # Redis settings
    redis_host: str
    redis_port: int

    # RabbitMQ settings
    rabbitmq_user: str
    rabbitmq_pass: SecretStr
    rabbitmq_host: str
    rabbitmq_port: int

    @property
    def celery_broker_url(self) -> str:
        return f'amqp://{self.rabbitmq_user}:{self.rabbitmq_pass.get_secret_value()}@{self.rabbitmq_host}:{self.rabbitmq_port}//'

    @property
    def celery_result_backend(self) -> str:
        return f'redis://{self.redis_host}:{self.redis_port}/0'

    @property
    def cache_location(self) -> str:
        return f'redis://{self.redis_host}:{self.redis_port}/1'

    class Config:
        case_sensitive = False
        env_file = '.env'
        extra = 'ignore'


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables based on file existence
if os.path.exists(BASE_DIR / '.env.dev'):
    env_file = BASE_DIR / '.env.dev'  # For local development
else:
    env_file = BASE_DIR / '.env'  # For containers

# Initialize settings
settings = AppSettings(_env_file=env_file)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-oqqlw^zfz#+ezt#tl9qp$lwztpq29qvw6)_#2n^gbqzgz+7p7%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'ninja',
    'django_celery_beat',
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'blurifier.urls'

TEMPLATES = [
    # DjangoTemplates backend (required for admin)
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    # Jinja2 backend (optional)
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'blurifier.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': settings.db_name,
        'USER': settings.db_user,
        'PASSWORD': settings.db_pass.get_secret_value(),
        'HOST': settings.db_host,
        'PORT': settings.db_port,
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery config
CELERY_BROKER_URL = settings.celery_broker_url
CELERY_RESULT_BACKEND = settings.celery_result_backend
CELERY_TASK_TIME_LIMIT = 28 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 2 * 60

CELERY_BEAT_SCHEDULE = {
    'process_unprocessed_texts': {
        'task': 'core.tasks.process_unprocessed_texts',
        'schedule': 120,
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': settings.cache_location,
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'custom': {
            'format': '[%(asctime)s] [%(process)d] [%(name)s] [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'custom',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Debug Toolbar Configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}
