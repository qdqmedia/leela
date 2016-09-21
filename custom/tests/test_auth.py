from unittest import TestCase
from unittest.mock import patch

from ldap3.core.exceptions import LDAPBindError
from django.contrib.auth.models import User

from custom.auth import LDAPBackend


class LDAPBackendTest(TestCase):

    def setUp(self):
        self.backend = LDAPBackend()

    def tearDown(self):
        User.objects.all().delete()

    @patch('custom.auth.Connection')
    def test_authentication_fail_user_no_exists(self, Connection_mock):
        def side(*arg, **kwargs):
            # Hack because normal attributes on the mock don't work
            Connection_mock.response = []
            return Connection_mock

        Connection_mock.side_effect = side
        user = self.backend.authenticate('jforcada', 'trololo')
        self.assertIsNone(user)

    @patch('custom.auth.Connection')
    def test_authentication_fail_user_bad_credentials(self, Connection_mock):
        def side(*arg, **kwargs):
            # Hack because normal attributes on the mock don't work
            if kwargs['user'] == 'tralala':
                raise LDAPBindError
            else:
                Connection_mock.response = [{'dn': 'tralala'}]
            return Connection_mock

        Connection_mock.side_effect = side
        user = self.backend.authenticate('jforcada', 'trololo')
        self.assertIsNone(user)

    @patch('custom.auth.Connection')
    def test_authentication_success(self, Connection_mock):
        def side(*arg, **kwargs):
            # Hack because normal attributes on the mock don't work
            if kwargs['user'] == 'tralala':
                Connection_mock.response = [{'attributes': {
                    'mail': 'jforcada@tuenti.com',
                    'givenName': 'Jaime',
                    'sn': 'Forcada Balaguer'
                }}]
            else:
                Connection_mock.response = [{'dn': 'tralala'}]
            return Connection_mock

        Connection_mock.side_effect = side
        user = self.backend.authenticate('jforcada', 'trololo')
        self.assertEqual('jforcada', user.username)
        self.assertEqual('Jaime', user.first_name)
        self.assertEqual('Forcada Balaguer', user.last_name)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
