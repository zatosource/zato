# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase
from unittest.mock import patch

# Zato
from zato.common.api import EnvVariable, HTTP_SOAP, SEC_DEF_TYPE, URL_TYPE
from zato.common.exception import BackendInvocationError, BadRequest
from zato.common.typing_ import cast_
from zato.server.connection.http_soap.outgoing import HTTPSOAPWrapper, Masked_Value

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

_invocation = HTTP_SOAP.Invocation

class ModuleCtx:
    CID = 'abc-123'
    Conn_Name = 'CRM and Billing'
    Host = 'https://example.com'

# ################################################################################################################################
# ################################################################################################################################

def _get_wrapper(config_extra:'stranydict | None'=None) -> 'HTTPSOAPWrapper':
    """ Builds a wrapper around a minimal connection config.
    """
    config = {
        'name': ModuleCtx.Conn_Name,
        'is_active': True,
        'is_internal': True,
        'timeout': 1,
        'username': 'my-user',
        'password': '',
        'orig_username': None,
        'sec_type': None,
        'security_name': None,
        'content_type': '',
        'data_format': 'json',
        'transport': URL_TYPE.PLAIN_HTTP,
        'address_host': ModuleCtx.Host,
        'address_url_path': '/api',
        'pool_size': 1,
        'validate_tls': True,
        'tls_client_cert': None,
        'tls_client_key': None,
    }

    if config_extra:
        config.update(config_extra)

    out = HTTPSOAPWrapper(cast_('any_', None), config)
    return out

# ################################################################################################################################
# ################################################################################################################################

class PathParamTestCase(TestCase):
    """ Tests how the values of path parameters are placed into an address.
    """

    def _format(self, url_path:'str', params:'stranydict') -> 'str':
        wrapper = _get_wrapper({'address_url_path': url_path})

        address, _ = wrapper.format_address(ModuleCtx.CID, params)
        return address

# ################################################################################################################################

    def test_plain_value(self) -> 'None':
        address = self._format('/api/{customer}/orders', {'customer': 'abc'})

        self.assertEqual(address, f'{ModuleCtx.Host}/api/abc/orders')

# ################################################################################################################################

    def test_value_cannot_leave_its_own_segment(self) -> 'None':

        # A value spelled as a relative path names no directory above the one it is in
        address = self._format('/api/{customer}/orders', {'customer': '../../admin'})

        self.assertEqual(address, f'{ModuleCtx.Host}/api/..%2F..%2Fadmin/orders')

# ################################################################################################################################

    def test_value_cannot_add_a_segment(self) -> 'None':
        address = self._format('/api/{customer}/orders', {'customer': 'abc/def'})

        self.assertEqual(address, f'{ModuleCtx.Host}/api/abc%2Fdef/orders')

# ################################################################################################################################

    def test_value_cannot_leave_its_segment_through_an_encoded_slash(self) -> 'None':

        # A percent sign in a value is a percent sign, so a value that arrives already encoded
        # cannot be decoded by the endpoint into something that leaves the segment.
        address = self._format('/api/{customer}/orders', {'customer': '%2e%2e%2fadmin'})

        self.assertEqual(address, f'{ModuleCtx.Host}/api/%252e%252e%252fadmin/orders')

# ################################################################################################################################

    def test_value_cannot_add_a_query_string(self) -> 'None':
        address = self._format('/api/{customer}/orders', {'customer': 'abc?admin=1'})

        self.assertEqual(address, f'{ModuleCtx.Host}/api/abc%3Fadmin%3D1/orders')

# ################################################################################################################################

    def test_what_is_left_becomes_the_query_string(self) -> 'None':
        wrapper = _get_wrapper({'address_url_path': '/api/{customer}/orders'})
        params = {'customer': 'abc', 'page': '2'}

        address, qs_params = wrapper.format_address(ModuleCtx.CID, params)

        self.assertEqual(address, f'{ModuleCtx.Host}/api/abc/orders')
        self.assertDictEqual(qs_params, {'page': '2'})

        # The caller's own dict is never written into
        self.assertDictEqual(params, {'customer': 'abc', 'page': '2'})

# ################################################################################################################################

    def test_missing_path_param_is_reported(self) -> 'None':
        wrapper = _get_wrapper({'address_url_path': '/api/{customer}/orders'})

        with self.assertRaises(BadRequest):
            _ = wrapper.format_address(ModuleCtx.CID, {'page': '2'})

# ################################################################################################################################
# ################################################################################################################################

class MissingPasswordTestCase(TestCase):
    """ Tests what a connection does when its password was never provided - an import leaves
    a placeholder behind for a value whose environment variable was not set.
    """
    def _get_placeholder(self) -> 'str':
        out = f'{EnvVariable.Missing_Value_Prefix}My_Token_abc123def456'
        return out

# ################################################################################################################################

    def test_placeholder_is_noticed(self) -> 'None':
        placeholder = self._get_placeholder()
        wrapper = _get_wrapper({'sec_type': SEC_DEF_TYPE.BASIC_AUTH, 'password': placeholder})

        self.assertEqual(wrapper.missing_password, placeholder)

# ################################################################################################################################

    def test_invocation_is_refused(self) -> 'None':
        placeholder = self._get_placeholder()
        wrapper = _get_wrapper({'sec_type': SEC_DEF_TYPE.BASIC_AUTH, 'password': placeholder})

        with self.assertRaises(BackendInvocationError) as raised:
            _ = wrapper.invoke_http(ModuleCtx.CID, 'GET', wrapper.address, '', {}, None)

        self.assertIn(ModuleCtx.Conn_Name, raised.exception.args[0])
        self.assertIn(placeholder, raised.exception.args[0])

# ################################################################################################################################

    def test_a_password_that_was_provided_is_not_a_placeholder(self) -> 'None':
        wrapper = _get_wrapper({'sec_type': SEC_DEF_TYPE.BASIC_AUTH, 'password': 'my-password'})

        self.assertEqual(wrapper.missing_password, '')

# ################################################################################################################################
# ################################################################################################################################

class ConfigNoSensitiveTestCase(TestCase):
    """ Tests what a connection's configuration looks like on its way to a log.
    """

    def test_secrets_are_masked(self) -> 'None':
        config_extra = {
            'password': 'my-password',
            _invocation.Field_Request_Headers: 'X-My-Token=abc123',
            _invocation.Field_Request_Query_String: 'api_key=abc123',
            _invocation.Field_Request_Data: '{"token":"abc123"}',
        }

        wrapper = _get_wrapper(config_extra)
        config_no_sensitive = wrapper.config_no_sensitive

        self.assertEqual(config_no_sensitive['password'], Masked_Value)
        self.assertEqual(config_no_sensitive[_invocation.Field_Request_Headers], Masked_Value)
        self.assertEqual(config_no_sensitive[_invocation.Field_Request_Query_String], Masked_Value)
        self.assertEqual(config_no_sensitive[_invocation.Field_Request_Data], Masked_Value)

        # What is not a secret is still there to be read
        self.assertEqual(config_no_sensitive['name'], ModuleCtx.Conn_Name)
        self.assertEqual(config_no_sensitive['address_host'], ModuleCtx.Host)

        # The connection's own configuration is untouched
        self.assertEqual(wrapper.config['password'], 'my-password')

# ################################################################################################################################

    def test_fields_a_connection_does_not_have_are_not_added(self) -> 'None':
        wrapper = _get_wrapper()

        self.assertNotIn(_invocation.Field_Request_Headers, wrapper.config_no_sensitive)

# ################################################################################################################################
# ################################################################################################################################

class MTLSTestCase(TestCase):
    """ Tests what happens to a connection's pooled sockets when its certificate material changes.
    """

    def _get_mtls_wrapper(self) -> 'HTTPSOAPWrapper':
        out = _get_wrapper({
            'sec_type': SEC_DEF_TYPE.MTLS,
            'cert_path': '/tmp/first.crt.pem',
            'key_path': '/tmp/first.key.pem',
        })
        return out

# ################################################################################################################################

    def test_definition_material_is_used(self) -> 'None':
        wrapper = self._get_mtls_wrapper()

        self.assertEqual(wrapper.config['tls_client_cert'], '/tmp/first.crt.pem')
        self.assertEqual(wrapper.config['tls_client_key'], '/tmp/first.key.pem')

# ################################################################################################################################

    def test_pooled_connections_are_discarded(self) -> 'None':
        wrapper = self._get_mtls_wrapper()

        # The definition is edited to present a different certificate
        wrapper.config['cert_path'] = '/tmp/second.crt.pem'
        wrapper.config['key_path'] = '/tmp/second.key.pem'

        with patch.object(wrapper.https_adapter, 'clear_pool') as mock_clear_pool:
            wrapper.set_auth()

        mock_clear_pool.assert_called_once_with()
        self.assertEqual(wrapper.config['tls_client_cert'], '/tmp/second.crt.pem')

# ################################################################################################################################
# ################################################################################################################################

class ApiKeyHeaderTestCase(TestCase):
    """ Tests the headers that an API key definition contributes.
    """

    def test_header_name_is_not_kept_after_a_rename(self) -> 'None':
        wrapper = _get_wrapper({
            'sec_type': SEC_DEF_TYPE.APIKEY,
            'orig_username': 'X-My-Token',
            'password': 'abc123',
        })

        self.assertDictEqual(wrapper.base_headers, {'X-My-Token': 'abc123'})

        # The definition is edited to use a different header name
        wrapper.config['orig_username'] = 'X-My-Other-Token'
        wrapper.set_auth()

        self.assertDictEqual(wrapper.base_headers, {'X-My-Other-Token': 'abc123'})

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
