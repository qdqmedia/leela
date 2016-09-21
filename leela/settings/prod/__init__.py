from ..custom import *
import os

DEBUG = False


CURRENT_HOST = ''


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('PG_DATABASE', 'nodb'),
        'USER': os.getenv('PG_USER', 'nouser'),
        'PASSWORD': os.getenv('PG_PASSWORD', 'nopass'),
        'HOST': os.getenv('PG_HOST', '127.0.0.1'),
        'PORT': os.getenv('PG_PORT', '5432')
    }
}


# Even in prod, let's serve media files from django
MEDIA_ROOT = '/media'
MEDIA_URL = '/media/'


RAVEN_CONFIG = {
    'dsn': os.getenv('SENTRY_DSN_SECRET', ''),
}
LOGGING['handlers']['sentry'] = {
    'level': 'WARNING',
    'class': 'raven.handlers.logging.SentryHandler',
    'dsn': RAVEN_CONFIG['dsn'],
}


# Queue configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', '')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT')) if os.getenv('RABBITMQ_PORT') else None
RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME', '')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', '')
RABBITMQ_CONNECTION_ATTEMPTS = 3
RABBITMQ_EMAIL_EXCHANGE = 'root'
RABBITMQ_ENQUEUE_EMAIL_QUEUE = 'email_leela'
RABBITMQ_PASSIVE = True

STATSD_ENABLED = True
