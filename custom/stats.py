from django.conf import settings
from statsd import StatsClient

client = None
if settings.STATSD_ENABLED:
    client = StatsClient(
        settings.STATSD_HOST,
        settings.STATSD_PORT,
        prefix=settings.STATSD_PREFIX,
        maxudpsize=settings.STATSD_MAXUDPSIZE
    )

def increment(metric, value=1):
    if settings.STATSD_ENABLED:
        client.incr(metric, value)

def gauge(metric, value):
    if settings.STATSD_ENABLED:
        client.gauge(metric, value)
