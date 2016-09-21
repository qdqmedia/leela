import time
import json
import logging
import requests
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.conf import settings

from emails.models import EmailEntry
from emails.security import is_spam
from emails.render import render_html, render_plain
from emails.backends import send_with_backend
from custom.stats import increment


logger = logging.getLogger('emails')
send_logger = logging.getLogger('sender')

def send_entries():
    """
    Takes all the not sent entries, and send them if they are ready.
    """
    now_ts = int(time.mktime(timezone.now().timetuple()))
    entries = EmailEntry.objects.filter(sent=False)\
                                .filter(is_spam=False)\
                                .filter(thirdparty_reject='')\
                                .filter(kind__active=True)
    sent_count = 0
    for entry in entries:
        if can_send(entry, now_ts):
            try:
                if is_spam(entry):
                    entry.is_spam = True
                    entry.save()
                    increment(settings.METRIC['SEND_IS_SPAM'])
                    continue

                if send(entry):
                    sent_count += 1
                    increment(settings.METRIC['SEND_OK'])
                    send_logger.info('[sender] Send OK. Entry id: {}'.format(entry.id))
                else:
                    log_send_error(entry)
            except Exception:
                log_send_error(entry)
    return sent_count

def log_send_error(entry):
    increment(settings.METRIC['SEND_FAIL'])
    logger.exception("An entry could not be sent: {}".format(entry.id))
    send_logger.info('[sender] Send FAIL. Entry id: {}'.format(entry.id))

def can_send(entry, now_ts):
    return time_arrived(entry.send_at, now_ts) and allowed_by_origin(entry)


def time_arrived(send_at, now_ts):
    """
    Returns True if there is not send_at value or if there is, and has
    passed.
    @type send_at: int timestamp in utc
    @type now: int timestamp in UTC
    """
    if send_at is None:
        return True

    return send_at <= now_ts


def allowed_by_origin(entry):
    """
    Returns True if there is not url value or if there is, and a
    GET request to it returns 200, {"allowed": true}

    Will mark the entry for deletion if {"allowed": false, "delete": true}

    TODO: make this an EmailEntry method
    """
    if not entry.check_url:
        return True

    allowed = False
    response = requests.get(entry.check_url)
    response.enconding = 'utf-8'
    parsed_response = json.loads(response.text)
    if response.status_code == 200:
        allowed = parsed_response.get('allowed', False)
        delete = parsed_response.get('delete', False)
        if delete:
            entry.deleted = True
            entry.save()
    else:
        logger.warning('There was an error checking url: {url} for emailentry {ee} of kind {ek}'\
            .format(url=entry.url, ee=entry.id, ek=entry.kind))

    return allowed


def send(emailentry):
    """
    Sends the email entry through the configured email backend.
    @type emailentry: EmailEntry
    """
    plain_body = render_plain(emailentry.kind, emailentry.context)
    rich_body = render_html(emailentry.kind, emailentry.context)

    email = EmailMultiAlternatives(
        subject=emailentry.subject,
        body=plain_body,
        to=emailentry.recipients.split(','),
        from_email=emailentry.sender,
        reply_to=emailentry.reply_to.split(',')
    )
    email.encoding = 'utf-8'

    # Attach HTML alternative
    if rich_body:
        email.attach_alternative(rich_body, 'text/html')

    # Attach already embedded images. Only the actually used ones.
    for img in emailentry.kind.iter_all_images():
        content_id = img.content_id[1:-1]
        if content_id in rich_body:
            image = MIMEImage(img.image.read())
            image.add_header('Content-ID', content_id)
            email.attach(image)

    # Attach regular files
    for att in emailentry.attachments.all():
        email.attach(
            filename=att.name,
            content=att.attached_file.read(),
            mimetype=att.content_type
        )
        increment(settings.METRIC['SEND_ATTACHS'])

    # Attach fixed metadata and extras provided by the entry
    email.metadata = {
        'customer_id': emailentry.customer_id,
        'kind': str(emailentry.kind),
        'email_id': emailentry.id
    }
    if len(emailentry.metadata) > 0:
        email.metadata.update(emailentry.metadata)

    sent = send_with_backend(email, emailentry)
    if not sent:
        return None
    return email
