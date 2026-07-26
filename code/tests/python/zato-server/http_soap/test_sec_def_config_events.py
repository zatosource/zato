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
from zato.server.connection.http_soap.url_data import URLData

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

_security_id = 201

_old_name = 'test.definition.old'
_new_name = 'test.definition.new'

_username = 'orders.client'
_password = 'password-0001'

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

def _make_definition(name:'str', has_password:'bool'=True) -> 'anydict':
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
# ################################################################################################################################

class SecretCarryingEditTestCase(TestCase):
    """ An edit of a definition whose secret does not travel with the edit itself, so it comes from
    what the server holds already - and an edit for a name the server holds nothing under is one
    the handler has to answer for rather than stop half way through.
    """

# ################################################################################################################################

    def test_an_edit_carries_the_secret_over(self) -> 'None':
        url_data = _make_url_data()
        url_data.basic_auth_config[_old_name] = _make_definition(_old_name)

        url_data.on_config_event_SECURITY_BASIC_AUTH_EDIT(_make_edit_msg())

        self.assertNotIn(_old_name, url_data.basic_auth_config)

        config = url_data.basic_auth_config[_new_name]['config']
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
        url_data.basic_auth_config[other_name] = _make_definition(other_name)

        url_data.on_config_event_SECURITY_BASIC_AUTH_EDIT(_make_edit_msg())

        # The handler returned rather than raising part way through it
        self.assertIn(other_name, url_data.basic_auth_config)

# ################################################################################################################################

    def test_an_edit_that_does_not_rename_still_works(self) -> 'None':
        url_data = _make_url_data()
        url_data.basic_auth_config[_old_name] = _make_definition(_old_name)

        msg = _make_edit_msg()
        msg.name = _old_name

        url_data.on_config_event_SECURITY_BASIC_AUTH_EDIT(msg)

        config = url_data.basic_auth_config[_old_name]['config']
        self.assertEqual(config['password'], _password)

# ################################################################################################################################
# ################################################################################################################################

class SelfContainedEditTestCase(TestCase):
    """ An edit of a definition that travels whole, so nothing has to be read out of the old entry.
    """

# ################################################################################################################################

    def test_an_edit_of_something_never_cached_still_lands(self) -> 'None':
        url_data = _make_url_data()

        msg = _make_edit_msg()
        msg.header = 'X-API-Key'
        msg.password = 'key-value-0001'
        msg.sec_type = SEC_DEF_TYPE.APIKEY

        url_data.on_config_event_SECURITY_APIKEY_EDIT(msg)

        # The edit brought everything with it, so the server has the definition under its new name
        self.assertIn(_new_name, url_data.apikey_config)
        self.assertNotIn(_old_name, url_data.apikey_config)

# ################################################################################################################################

    def test_an_edit_replaces_what_was_cached(self) -> 'None':
        url_data = _make_url_data()

        msg = _make_edit_msg()
        msg.header = 'X-API-Key'
        msg.password = 'key-value-0001'
        msg.sec_type = SEC_DEF_TYPE.APIKEY

        url_data.apikey_config[_old_name] = _make_definition(_old_name)
        url_data.on_config_event_SECURITY_APIKEY_EDIT(msg)

        self.assertIn(_new_name, url_data.apikey_config)
        self.assertNotIn(_old_name, url_data.apikey_config)

# ################################################################################################################################

    def test_the_id_index_follows_the_edit(self) -> 'None':
        url_data = _make_url_data()

        msg = _make_edit_msg()
        msg.header = 'X-API-Key'
        msg.password = 'key-value-0001'
        msg.sec_type = SEC_DEF_TYPE.APIKEY

        url_data.on_config_event_SECURITY_APIKEY_EDIT(msg)

        sec_def = url_data.apikey_get_by_id(_security_id)
        self.assertEqual(sec_def['name'], _new_name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
