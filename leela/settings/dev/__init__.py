from ..custom import *
import os
import sys
import logging


DEBUG = True

MEDIA_ROOT = "/qdq/media"
MEDIA_URL = '/media/'
STATIC_ROOT = '/qdq/static'
STATIC_URL = '/static/'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': os.getenv('DB_PORT_5432_TCP_ADDR', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT_5432_TCP_PORT', '5432')
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.file'


# Disable logging when running tests to avoid cluttered output.
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)


# Queue system
RABBITMQ_HOST = os.getenv('QUEUE_PORT_5672_TCP_ADDR')
RABBITMQ_PORT = int(os.getenv('QUEUE_PORT_5672_TCP_PORT'))
RABBITMQ_USERNAME = 'guest'
RABBITMQ_PASSWORD = 'guest'
RABBITMQ_CONNECTION_ATTEMPTS = 1
RABBITMQ_EMAIL_EXCHANGE = 'root'
RABBITMQ_ENQUEUE_EMAIL_QUEUE = 'enqueue-email'
RABBITMQ_PASSIVE = False

STATSD_ENABLED = False


LOGGING['handlers']['console']['level'] = 'DEBUG'

LOGGING['loggers']['MIDDLE'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}