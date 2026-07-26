# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from base64 import b64encode
from unittest import main, TestCase
from unittest.mock import MagicMock

# Zato
from zato.server.service.internal.pubsub.rest import PubSubRESTService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

_cid = 'zcid-test-0001'

_sec_name = 'orders.definition'
_username = 'orders.client'
_password = 'password-0001'

# ################################################################################################################################
# ################################################################################################################################

class _CountingDict(dict):
    """ A dict that says which keys were asked for.
    """
    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)
        self.keys_read = []

    def get(self, key:'any_', default:'any_'=None) -> 'any_':
        self.keys_read.append(key)
        return super().get(key, default)

# ################################################################################################################################
# ################################################################################################################################

def _make_sec_def(
    name:'str'=_sec_name,
    username:'str'=_username,
    password:'str'=_password,
    is_active:'bool'=True
) -> 'stranydict':

    out = {
        'config': {
            'id': 101,
            'name': name,
            'username': username,
            'password': password,
            'is_active': is_active,
        }
    }

    return out

# ################################################################################################################################

def _make_service(
    sec_defs:'stranydict',
    registered:'stranydict',
    auth_username:'str'=_username,
    auth_password:'str'=_password
) -> 'PubSubRESTService':
    """ A pub/sub REST service with the credential stores it reads filled in.
    """
    # The service machinery is of no interest here, only what authentication reads
    out = object.__new__(PubSubRESTService)

    out.cid = _cid # type: ignore[misc]

    credentials = f'{auth_username}:{auth_password}'.encode('utf8')
    encoded = b64encode(credentials).decode('utf8')

    out.wsgi_environ = {'HTTP_AUTHORIZATION': 'Basic ' + encoded} # type: ignore[misc]

    server = MagicMock()
    server.pubsub_subscriptions.get_sec_name_by_username.side_effect = registered.get
    server.config_manager.request_dispatcher.url_data.basic_auth_config = sec_defs

    out.server = server # type: ignore[misc]

    return out

# ################################################################################################################################
# ################################################################################################################################

class PubSubRESTCredentialsTestCase(TestCase):

    def test_a_registered_client_signs_in(self):

        sec_defs = _CountingDict({_sec_name: _make_sec_def()})
        service = _make_service(sec_defs, {_username: _sec_name})

        self.assertTrue(service._validate_credentials(_username))

    def test_only_the_definition_of_the_username_is_looked_at(self):

        # Definitions of other clients that must not be reached ..
        sec_defs = _CountingDict({
            'other.definition.1': _make_sec_def('other.definition.1', 'other.client.1', 'password-0002'),
            _sec_name: _make_sec_def(),
            'other.definition.2': _make_sec_def('other.definition.2', 'other.client.2', 'password-0003'),
        })

        service = _make_service(sec_defs, {_username: _sec_name})

        # .. and the one the username belongs to is the only one asked for.
        self.assertTrue(service._validate_credentials(_username))
        self.assertListEqual(sec_defs.keys_read, [_sec_name])

    def test_a_wrong_password_is_refused(self):

        sec_defs = _CountingDict({_sec_name: _make_sec_def()})
        service = _make_service(sec_defs, {_username: _sec_name}, auth_password='password-0009')

        self.assertFalse(service._validate_credentials(_username))

    def test_a_username_that_is_no_pubsub_client_is_refused(self):

        sec_defs = _CountingDict({_sec_name: _make_sec_def()})

        # The store knows of nobody, so the definitions are never consulted
        service = _make_service(sec_defs, {})

        self.assertFalse(service._validate_credentials(_username))
        self.assertListEqual(sec_defs.keys_read, [])

    def test_a_client_of_another_definition_type_is_refused(self):

        # A pub/sub client whose definition is not a Basic Auth one has nothing to be reached with here
        sec_defs = _CountingDict({})
        service = _make_service(sec_defs, {_username: 'apikey.definition'})

        self.assertFalse(service._validate_credentials(_username))

    def test_an_inactive_definition_is_refused(self):

        sec_defs = _CountingDict({_sec_name: _make_sec_def(is_active=False)})
        service = _make_service(sec_defs, {_username: _sec_name})

        self.assertFalse(service._validate_credentials(_username))

    def test_a_definition_with_no_credentials_is_refused(self):

        sec_defs = _CountingDict({_sec_name: _make_sec_def(password='')})
        service = _make_service(sec_defs, {_username: _sec_name})

        self.assertFalse(service._validate_credentials(_username))

    def test_the_username_of_the_definition_has_to_match_too(self):

        # A definition that carries another username is not the caller's, no matter what the store says
        sec_defs = _CountingDict({_sec_name: _make_sec_def(username='orders.client.renamed')})
        service = _make_service(sec_defs, {_username: _sec_name})

        self.assertFalse(service._validate_credentials(_username))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
