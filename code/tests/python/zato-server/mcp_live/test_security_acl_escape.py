# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pytest
import pytest

# local
from _client import MCPClient
from _constants import _error_method_not_found

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

# ################################################################################################################################
# ################################################################################################################################

# Maximum length for an extremely long service name
_max_service_name_length = 10000

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def client(zato_server:'any_') -> 'MCPClient':
    out = MCPClient(zato_server['mcp_url'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestACLEscape:
    """ Tests that service name manipulation cannot bypass the allowlist.
    """

    def test_path_traversal_in_service_name(self, client:'MCPClient') -> 'None':
        """ Path traversal in the service name must be rejected.
        """

        params = {'name': '../../zato.server.info', 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params)
        data = response.json()

        assert 'error' in data
        assert data['error']['code'] == _error_method_not_found

# ################################################################################################################################

    def test_null_byte_in_service_name(self, client:'MCPClient') -> 'None':
        """ Service name with embedded null bytes must be rejected.
        """

        params = {'name': 'demo.echo\x00zato.ping', 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params)
        data = response.json()

        assert 'error' in data
        assert data['error']['code'] == _error_method_not_found

# ################################################################################################################################

    def test_extremely_long_service_name(self, client:'MCPClient') -> 'None':
        """ An extremely long service name must be rejected without crashing.
        """

        long_name = 'a' * _max_service_name_length
        params = {'name': long_name, 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params)
        data = response.json()

        assert 'error' in data
        assert data['error']['code'] == _error_method_not_found

# ################################################################################################################################

    def test_case_variation_of_internal_service(self, client:'MCPClient') -> 'None':
        """ Internal services with case variations must still be rejected.
        """

        case_variants = ['Zato.Ping', 'ZATO.PING', 'ZaTo.PiNg']

        for variant in case_variants:
            params = {'name': variant, 'arguments': {}}
            response = client.jsonrpc('tools/call', params=params)
            data = response.json()

            assert 'error' in data, f'Case variant {variant} was not rejected'
            assert data['error']['code'] == _error_method_not_found

# ################################################################################################################################

    def test_unicode_homoglyph_service_name(self, client:'MCPClient') -> 'None':
        """ Unicode homoglyphs of internal service names must be rejected.
        """

        # Cyrillic 'a' (U+0430) instead of Latin 'a' in 'zato'
        homoglyph_name = 'z\u0430to.ping'
        params = {'name': homoglyph_name, 'arguments': {}}
        response = client.jsonrpc('tools/call', params=params)
        data = response.json()

        assert 'error' in data
        assert data['error']['code'] == _error_method_not_found

# ################################################################################################################################
# ################################################################################################################################
