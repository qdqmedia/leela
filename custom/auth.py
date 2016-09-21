import logging

from ldap3 import (
    Server, GET_ALL_INFO, STRATEGY_SYNC, AUTH_SIMPLE, Connection,
    SEARCH_SCOPE_WHOLE_SUBTREE
)
from ldap3.core.exceptions import LDAPBindError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.conf import settings


logger = logging.getLogger('authentication')


class LDAPBackend(object):
    """
    Authenticates against the LDAP service defined by the settings:
      - LDAP_AUTH_SERVER_URI
      - LDAP_BIND_USER
      - LDAP_BIND_PASSWORD
      - LDAP_PORT
      - LDAP_SEARCH_BASE
      - LDAP_ACCOUNT_FILTER

    In case of success, creates a user in the system based on the info
    provided by LDAP, so the next time the user logs in only the
    django.contrib.auth.backends.ModelBackend (the django build in auth
    backend) is checked if configured in AUTHENTICATION_BACKENDS first.
    """

    def authenticate(self, username=None, password=None):
        user = None
        user_dn = self._get_user_dn(username)
        if user_dn is not None:
            user_record = self._check_credentials(user_dn, username, password)
            if user_record is not None:
                user = self._create_user(username, password, user_record)
        return user

    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def _get_user_dn(self, username):
        server = Server(settings.LDAP_AUTH_SERVER_URI, port=settings.LDAP_PORT,
                        get_info=GET_ALL_INFO)
        try:
            connection = Connection(
                server,
                auto_bind=False,
                user=settings.LDAP_BIND_USER,
                password=settings.LDAP_BIND_PASSWORD,
                client_strategy = STRATEGY_SYNC,
                authentication=AUTH_SIMPLE,
                check_names=True
            )
            connection.bind(read_server_info=False)
        except LDAPBindError:
            logger.exception("Error binding connection to LDAP server.")
            return None

        connection.search(
            search_base=settings.LDAP_SEARCH_BASE,
            search_filter=settings.LDAP_ACCOUNT_FILTER.format(username),
            search_scope=SEARCH_SCOPE_WHOLE_SUBTREE,
            attributes=[]
        )
        response = connection.response
        connection.unbind()
        if len(response) > 0:
            return response[0]['dn']
        else:
            return None

    def _check_credentials(self, user_dn, username, password):
        server = Server(settings.LDAP_AUTH_SERVER_URI, port=settings.LDAP_PORT,
                        get_info=GET_ALL_INFO)
        try:
            connection = Connection(
                server,
                auto_bind=False,
                user=user_dn,
                password=password,
                client_strategy = STRATEGY_SYNC,
                authentication=AUTH_SIMPLE,
                check_names=True
            )
            connection.bind(read_server_info=False)
        except LDAPBindError:
            logger.exception("Error binding connection to LDAP server.")
            return None

        connection.search(
            search_base=settings.LDAP_SEARCH_BASE,
            search_filter=settings.LDAP_ACCOUNT_FILTER.format(username),
            search_scope=SEARCH_SCOPE_WHOLE_SUBTREE,
            attributes=['givenName', 'sn', 'mail']
        )
        response = connection.response
        connection.unbind()
        if len(response) > 0:
            return response[0]
        else:
            return None

    def _create_user(self, username, password, user_record):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'password': make_password(password),
                'email': user_record['attributes']['mail'],
                'first_name': user_record['attributes']['givenName'],
                'last_name': user_record['attributes']['sn'],
                'is_staff': True,
                'is_superuser': True
            }
        )
        return user
