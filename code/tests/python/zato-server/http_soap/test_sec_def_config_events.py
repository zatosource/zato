# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import MagicMock

# Zato
from zato.common.api import SEC_DEF_TYPE
from zato.common.ext.bunch import Bunch
from zato.common.typing_ import cast_
from zato.server.connection.http_soap import Unauthorized
from zato.server.connection.http_soap.url_data import URLData

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_security_id = 201

_old_name = 'test.definition.old'
_new_name = 'test.definition.new'

_username = 'orders.client'
_password = 'password-0001'

_apikey_header = 'X-API-Key'
_apikey_value  = 'key-value-0001'

# The header under which a request presents the API key, as the WSGI environment has it
_apikey_wsgi_header = 'HTTP_X_API_KEY'

_cid = 'test-cid-0001'
_match_target = '/api/orders'

# ################################################################################################################################
# ################################################################################################################################

def _make_url_data() -> 'URLData':
    """ A URLData whose definition configuration is real and whose surroundings are mocked out.
    """
    out = URLData(
        MagicMock(),
        channel_data=[],
        url_sec={},
        basic_auth_config={},
        mtls_config={},
        ntlm_config={},
        oauth_config={},
        spnego_config={},
        apikey_config={},
        wss_config={},
    )

    return out

# ################################################################################################################################

def _make_definition(name:'str', has_password:'bool'=True) -> 'Bunch':
    """ What a definition looks like once it is cached, i.e. a config under a name of its own.
    """
    config = Bunch()
    config.id = _security_id
    config.name = name
    config.username = _username
    config.sec_type = SEC_DEF_TYPE.BASIC_AUTH

    if has_password:
        config.password = _password

    out = Bunch()
    out.config = config

    return out

# ################################################################################################################################

def _make_edit_msg() -> 'Bunch':
    """ What an edit sends, which is the definition without its secret.
    """
    out = Bunch()
    out.id = _security_id
    out.old_name = _old_name
    out.name = _new_name
    out.username = _username
    out.sec_type = SEC_DEF_TYPE.BASIC_AUTH

    return out

# ################################################################################################################################

def _make_apikey_edit_msg() -> 'Bunch':
    """ What the API key edit service publishes - the definition and its header, never the key.
    """
    out = _make_edit_msg()
    out.header = _apikey_header
    out.sec_type = SEC_DEF_TYPE.APIKEY

    return out

# ################################################################################################################################

def _make_apikey_definition(name:'str') -> 'Bunch':
    """ What a cached API key looks like, its key included.
    """
    out = _make_definition(name)
    out.config.sec_type = SEC_DEF_TYPE.APIKEY
    out.config.header = _apikey_header
    out.config.password = _apikey_value

    return out

# ################################################################################################################################
# ################################################################################################################################

class SecretCarryingEditTestCase(TestCase):
    """ An edit of a definition whose secret does not travel with the edit itself, so it comes from
    what the server holds already - and an edit for a name the server holds nothing under is one
    the handler has to answer for rather than stop half way through.
    """

# ################################################################################################################################

    def test_an_edit_carries_the_secret_over(self) -> 'None':
        url_data = _make_url_data()
        cast_('anydict', url_data.basic_auth_config)[_old_name] = _make_definition(_old_name)

        url_data.on_config_event_SECURITY_BASIC_AUTH_EDIT(_make_edit_msg())

        self.assertNotIn(_old_name, cast_('any_', url_data.basic_auth_config))

        config = cast_('any_', url_data.basic_auth_config)[_new_name]['config']
        self.assertEqual(config['password'], _password)
        self.assertEqual(config['name'], _new_name)

# ################################################################################################################################

    def test_an_edit_of_something_never_cached_is_refused(self) -> 'None':
        url_data = _make_url_data()

        url_data.on_config_event_SECURITY_BASIC_AUTH_EDIT(_make_edit_msg())

        # Nothing was stored, since there was no secret here for the edit to go on with
        self.assertEqual(url_data.basic_auth_config, {})

# ################################################################################################################################

    def test_an_edit_of_something_never_cached_leaves_the_rest_alone(self) -> 'None':
        url_data = _make_url_data()

        other_name = 'test.definition.other'
        cast_('anydict', url_data.basic_auth_config)[other_name] = _make_definition(other_name)

        url_data.on_config_event_SECURITY_BASIC_AUTH_EDIT(_make_edit_msg())

        # The handler returned rather than raising part way through it
        self.assertIn(other_name, cast_('any_', url_data.basic_auth_config))

# ################################################################################################################################

    def test_an_edit_that_does_not_rename_still_works(self) -> 'None':
        url_data = _make_url_data()
        cast_('anydict', url_data.basic_auth_config)[_old_name] = _make_definition(_old_name)

        msg = _make_edit_msg()
        msg.name = _old_name

        url_data.on_config_event_SECURITY_BASIC_AUTH_EDIT(msg)

        config = cast_('any_', url_data.basic_auth_config)[_old_name]['config']
        self.assertEqual(config['password'], _password)

# ################################################################################################################################
# ################################################################################################################################

class APIKeyEditTestCase(TestCase):
    """ An edit of an API key, which the edit service publishes with the header but without the key itself,
    so the key comes from what the server holds already.
    """

# ################################################################################################################################

    def test_an_edit_carries_the_key_over(self) -> 'None':
        url_data = _make_url_data()
        cast_('anydict', url_data.apikey_config)[_old_name] = _make_apikey_definition(_old_name)

        url_data.on_config_event_SECURITY_APIKEY_EDIT(_make_apikey_edit_msg())

        self.assertNotIn(_old_name, cast_('any_', url_data.apikey_config))

        config = cast_('any_', url_data.apikey_config)[_new_name]['config']
        self.assertEqual(config['password'], _apikey_value)
        self.assertEqual(config['name'], _new_name)

# ################################################################################################################################

    def test_an_edit_that_does_not_rename_keeps_the_key(self) -> 'None':
        url_data = _make_url_data()
        cast_('anydict', url_data.apikey_config)[_old_name] = _make_apikey_definition(_old_name)

        msg = _make_apikey_edit_msg()
        msg.name = _old_name

        url_data.on_config_event_SECURITY_APIKEY_EDIT(msg)

        config = cast_('any_', url_data.apikey_config)[_old_name]['config']
        self.assertEqual(config['password'], _apikey_value)

# ################################################################################################################################

    def test_the_id_index_returns_the_key_after_the_edit(self) -> 'None':
        url_data = _make_url_data()
        cast_('anydict', url_data.apikey_config)[_old_name] = _make_apikey_definition(_old_name)

        url_data.on_config_event_SECURITY_APIKEY_EDIT(_make_apikey_edit_msg())

        # Security groups and the OpenAPI console read the definition by its ID, so the key has to be there too
        sec_def = cast_('any_', url_data.apikey_get_by_id(_security_id))
        self.assertEqual(sec_def['name'], _new_name)
        self.assertEqual(sec_def['password'], _apikey_value)

# ################################################################################################################################

    def test_an_edit_of_something_never_cached_is_refused(self) -> 'None':
        url_data = _make_url_data()

        url_data.on_config_event_SECURITY_APIKEY_EDIT(_make_apikey_edit_msg())

        # Nothing was stored, since there was no key here for the edit to go on with
        self.assertEqual(url_data.apikey_config, {})

# ################################################################################################################################
# ################################################################################################################################

class InactiveDefinitionTestCase(TestCase):
    """ A channel secured directly by a definition accepts no caller while the definition is not active.
    """

# ################################################################################################################################

    def _make_secured_url_data(self) -> 'URLData':
        """ A URLData with an active API key and a channel secured by it.
        """
        url_data = _make_url_data()

        msg = Bunch()
        msg.id = _security_id
        msg.name = _old_name
        msg.username = _username
        msg.sec_type = SEC_DEF_TYPE.APIKEY
        msg.header = _apikey_header
        msg.password = _apikey_value
        msg.is_active = True

        url_data.on_config_event_SECURITY_APIKEY_CREATE(msg)

        # The channel has a copy of the definition, as it does after the server starts
        cached = cast_('any_', url_data.apikey_config)[_old_name]

        sec_info = Bunch()
        sec_info.sec_def = Bunch(cached.config)

        cast_('anydict', url_data.url_sec)[_match_target] = sec_info

        return url_data

# ################################################################################################################################

    def _edit(self, url_data:'URLData', is_active:'bool') -> 'None':
        """ Publishes an edit of the API key with the given activation state.
        """
        msg = _make_apikey_edit_msg()
        msg.is_active = is_active

        url_data.on_config_event_SECURITY_APIKEY_EDIT(msg)

# ################################################################################################################################

    def _check(self, url_data:'URLData', enforce_auth:'bool'=True) -> 'any_':
        """ Runs the channel's security check against a request with the correct key.
        """
        sec = cast_('anydict', url_data.url_sec)[_match_target]
        request_ctx = {_apikey_wsgi_header: _apikey_value}
        config_manager = MagicMock()

        out = url_data.check_security(
            sec, _cid, {}, _match_target, b'', request_ctx, {}, config_manager, enforce_auth=enforce_auth)
        return out

# ################################################################################################################################

    def test_an_active_key_authenticates(self) -> 'None':
        url_data = self._make_secured_url_data()
        self._edit(url_data, True)

        self.assertTrue(self._check(url_data))

# ################################################################################################################################

    def test_a_key_deactivated_by_an_edit_is_refused(self) -> 'None':
        url_data = self._make_secured_url_data()
        self._edit(url_data, False)

        with self.assertRaises(Unauthorized):
            _ = self._check(url_data)

# ################################################################################################################################

    def test_a_key_activated_again_authenticates(self) -> 'None':
        url_data = self._make_secured_url_data()
        self._edit(url_data, False)

        # The second edit renames the definition back, so it is found under its original name again
        msg = _make_apikey_edit_msg()
        msg.old_name = _new_name
        msg.name = _old_name
        msg.is_active = True

        url_data.on_config_event_SECURITY_APIKEY_EDIT(msg)

        self.assertTrue(self._check(url_data))

# ################################################################################################################################

    def test_an_inactive_key_without_enforcement_does_not_authenticate(self) -> 'None':
        url_data = self._make_secured_url_data()
        self._edit(url_data, False)

        self.assertFalse(self._check(url_data, enforce_auth=False))

# ################################################################################################################################

    def test_an_inactive_basic_auth_definition_is_refused(self) -> 'None':
        url_data = _make_url_data()

        sec_def = _make_definition(_old_name).config
        sec_def.is_active = False

        sec = Bunch()
        sec.sec_def = sec_def

        with self.assertRaises(Unauthorized):
            _ = url_data.check_security(sec, _cid, {}, _match_target, b'', {}, {}, MagicMock())

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
