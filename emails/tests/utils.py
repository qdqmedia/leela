import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


def create_upload_image():
    fixture_path = os.path.join(settings.BASE_DIR, 'emails', 'tests',
                                'fixtures', 'test.jpg')
    raw_file = open(fixture_path, 'rb')
    uploaded_image = SimpleUploadedFile(
        'test.jpg',
        raw_file.read()
    )
    raw_file.close()
    uploaded_image.content_type = 'image/jpeg'
    return uploaded_image


def create_upload_file(path, content):
    raw_file = open(path, 'w')
    raw_file.write(content)
    raw_file.close()
    raw_file = open(path, 'rb')
    uploaded_file = SimpleUploadedFile(
        path.split('/')[-1],
        raw_file.read()
    )
    raw_file.close()
    return uploaded_file


def get_jpg_content():
    fixture_path = os.path.join(settings.BASE_DIR, 'emails', 'tests',
                                'fixtures', 'test.jpg')
    raw_file = open(fixture_path, 'rb')
    return raw_file.read()


class EmailBackendMockSuccess(BaseEmailBackend):
    response = None

    def send_messages(self, email_messages):
        for msg in email_messages:
            msg.response_content = [{'id': '348dj38dj28do5jd82'}]


class EmailBackendMockFailure(BaseEmailBackend):
    response = None

    def send_messages(self, email_messages):
        for msg in email_messages:
            msg.response_content = None


class ResponseManagerStub(object):
    def process_response(self, email, entry):
        if email.response_content is not None:
            entry.thirdparty_id = email.response_content[0]['id']
            return True
        return False


class EmailBackendMockReject(BaseEmailBackend):
    response = None

    def send_messages(self, email_messages):
        for msg in email_messages:
            msg.response_content = [{'rejected_because': 'potato'}]


class ResponseManagerRejectStub(object):
    def process_response(self, email, entry):
        entry.thirdparty_reject = email.response_content[0]['rejected_because']
        return False
