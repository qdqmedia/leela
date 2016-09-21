"""
This module manages the message consumtion from the queue system.
Current consumers are:
- Enqueue Email: Use to enqueue new emails.
"""
import pika
import json
import logging

from django.conf import settings

from emails.schedule import schedule
from custom.stats import increment


logger = logging.getLogger('emails')
sched_logger = logging.getLogger('scheduler')


def on_enqueue_email(channel, method_frame, header_frame, body):
    """Callback to email enqueue. Sends ack to Rabbit on success"""
    increment(settings.METRIC['CONSUMER_RECEIVED'])
    sched_logger.info('[scheduler] Starting enqueue: {}'.format(body))

    try:
        parsed_body = json.loads(body.decode('utf8'))
        schedule(
            name=parsed_body['name'],
            language=parsed_body['language'],
            params=parsed_body
        )
        
        increment(settings.METRIC['SCHEDULED_OK'])
        sched_logger.info('[scheduler] Finished enqueue: successful')
    except Exception:
        logger.exception('Exception ocurred during enqueuing')
        sched_logger.info('[scheduler] Finished enqueue: failure')
        increment(settings.METRIC['SCHEDULED_FAIL'])
    finally:
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        increment(settings.METRIC['CONSUMER_ACK'])


def send_email_consumer():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                virtual_host=settings.RABBITMQ_VHOST,
                credentials=pika.PlainCredentials(
                    username=settings.RABBITMQ_USERNAME,
                    password=settings.RABBITMQ_PASSWORD
                ),
                connection_attempts=settings.RABBITMQ_CONNECTION_ATTEMPTS,
                heartbeat_interval=settings.RABBITMQ_HEARTBEAT_INTERVAL,
                socket_timeout=1
            )
        )
        channel = connection.channel()

        if settings.DEBUG:
            # Declare the queue topology in a dev/test environment.
            channel.exchange_declare(exchange=settings.RABBITMQ_EMAIL_EXCHANGE,
                                     durable=True, passive=settings.RABBITMQ_PASSIVE)
            channel.queue_declare(queue=settings.RABBITMQ_ENQUEUE_EMAIL_QUEUE,
                                  durable=True, passive=settings.RABBITMQ_PASSIVE)

        channel.queue_bind(exchange=settings.RABBITMQ_EMAIL_EXCHANGE,
                           queue=settings.RABBITMQ_ENQUEUE_EMAIL_QUEUE)
    except Exception as e:
        logger.exception('Exception occurred while connecting to RabbitMQ')
        raise e

    sched_logger.info(' ** Waiting for emails to send. To exit press CTRL+C ** ')

    channel.basic_consume(on_enqueue_email,
        queue=settings.RABBITMQ_ENQUEUE_EMAIL_QUEUE, exclusive=False)
    channel.start_consuming()
