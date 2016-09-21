from .base import *

ALLOWED_HOSTS += ["*"]


# EmailKind allowed languages
LANGUAGES = (
    ('pt', 'Portuguese'),
    ('es', 'Spanish'),
)
DEFAULT_LANGUAGE_CODE = 'es'


DEFAULT_FROM_EMAIL = 'qdqteayuda@qdqmedia.com'


# Queue system
RABBITMQ_HOST = 'TODO'
RABBITMQ_PORT = int('0')
RABBITMQ_USERNAME = 'guest'
RABBITMQ_PASSWORD = 'guest'
RABBITMQ_CONNECTION_ATTEMPTS = 3
RABBITMQ_EMAIL_EXCHANGE = 'root'
RABBITMQ_ENQUEUE_EMAIL_QUEUE = 'enqueue-email'
RABBITMQ_PASSIVE = True
RABBITMQ_HEARTBEAT_INTERVAL = 10


# Spam configuration
SPAM_CHECK = {
    'solweb_contact': ('custom.spamchecks.has_href',)
}


# Custom template filters
FILTERS = (
    ('linebreaksbr', 'django.template.defaultfilters.linebreaksbr'),
    ('floatformat', 'django.template.defaultfilters.floatformat'),
    ('date', 'custom.filters.datetimeformat'),
    ('localize_money', 'custom.filters.localize_money')
)

# Email backends
CUSTOM_EMAIL_BACKENDS = (
    ('mandrill',
     'djrill.mail.backends.djrill.DjrillBackend',
     'custom.backends.MandrillResponseManager'
    ),
)

# Default backend
CUSTOM_DEFAULT_EMAIL_BACKEND = 'mandrill'

# Custom email backend configurations
MANDRILL_API_KEY = ''
MANDRILL_IGNORE_RECIPIENT_STATUS = True


# StatsD Metrics
STATSD_HOST = ''
STATSD_PORT = 8125
STATSD_PREFIX = 'app.leela'
STATSD_MAXUDPSIZE = 512


# The custom LDAP backend is not used, this setting are left here to support its tests
LDAP_AUTH_SERVER_URI = ''
LDAP_BIND_USER = ''
LDAP_BIND_PASSWORD = ''
LDAP_PORT = 389
LDAP_SEARCH_BASE = ''
LDAP_ACCOUNT_FILTER = ''
