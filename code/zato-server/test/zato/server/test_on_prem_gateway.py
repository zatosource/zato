# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import BAD_REQUEST, OK
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

# Zato
from zato.common.api import On_Prem_Gateway
from zato.server.on_prem_gateway import get_hub_admin_url, get_public_address, HubClient, OnPremGatewayManager, \
    parse_hosts

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anylist, strdict, strdictlist

    # Dummy assignments to satisfy type checkers
    anylist = anylist
    strdictlist = strdictlist

# ################################################################################################################################
# ################################################################################################################################

# What a gateway is called and what it reaches
_Gateway_Name = 'warsaw-office'
_Other_Gateway_Name = 'london-office'
_Erp_Address = 'erp-db.corp.local:5432'

# What the hub reports for an enrolled gateway
_Key_Fingerprint = 'SHA256:9z3Xk1Qm7RtP2wYd5Nc8Bv4Hs6Lj0Af2Ue7Ip3Or1Ty'
_Enrollment_Token = 'eyJhZGRyZXNzIjoiaHR0cHM6Ly96YXRvLmV4YW1wbGUuY29tOjExMjI0IiwibmFtZSI6Indhc'

# Where the hub's admin API is in these tests
_Hub_Admin_Url = 'http://127.0.0.1:11227'

# ################################################################################################################################
# ################################################################################################################################

def _get_response(status_code:'int', payload:'strdict') -> 'MagicMock':
    """ Builds what the requests library would return for one call to the hub.
    """
    is_ok = status_code < BAD_REQUEST

    out = MagicMock()
    out.ok = is_ok
    out.status_code = status_code
    out.text = str(payload)
    out.json.return_value = payload

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestParseHosts(TestCase):
    """ Validating the addresses on input.
    """

    def test_result_is_sorted_and_trimmed(self) -> 'None':

        result = parse_hosts(['  warehouse.corp.local:443  ', '', 'billing.corp.local:5432'])

        self.assertEqual(result, ['billing.corp.local:5432', 'warehouse.corp.local:443'])

# ################################################################################################################################

    def test_address_without_port_is_rejected(self) -> 'None':

        with self.assertRaises(Exception):
            _ = parse_hosts(['erp-db.corp.local'])

# ################################################################################################################################

    def test_address_without_numeric_port_is_rejected(self) -> 'None':

        with self.assertRaises(Exception):
            _ = parse_hosts(['erp-db.corp.local:postgresql'])

# ################################################################################################################################

    def test_port_outside_range_is_rejected(self) -> 'None':

        with self.assertRaises(Exception):
            _ = parse_hosts(['erp-db.corp.local:0'])

        with self.assertRaises(Exception):
            _ = parse_hosts(['erp-db.corp.local:70000'])

# ################################################################################################################################

    def test_duplicate_is_rejected(self) -> 'None':

        with self.assertRaises(Exception):
            _ = parse_hosts([_Erp_Address, _Erp_Address])

# ################################################################################################################################
# ################################################################################################################################

class TestPublicAddress(TestCase):
    """ The address an enrollment token points a gateway back at.
    """

    def setUp(self) -> 'None':
        self.previous = dict(os.environ)
        os.environ.clear()

# ################################################################################################################################

    def tearDown(self) -> 'None':
        os.environ.clear()
        os.environ.update(self.previous)

# ################################################################################################################################

    def test_explicit_setting_wins(self) -> 'None':

        os.environ[On_Prem_Gateway.Env.Public_Address] = 'https://api.example.com'

        result = get_public_address('dashboard.example.com:8183')

        self.assertEqual(result, 'https://api.example.com')

# ################################################################################################################################

    def test_derived_from_the_dashboard_host(self) -> 'None':

        os.environ['Zato_Port_Load_Balancer_SSL'] = '11224'

        result = get_public_address('zato.example.com:8183')

        self.assertEqual(result, 'https://zato.example.com:11224')

# ################################################################################################################################

    def test_nothing_to_derive_from_is_an_error(self) -> 'None':

        with self.assertRaises(Exception):
            _ = get_public_address(None)

# ################################################################################################################################

    def test_admin_url_follows_the_environment(self) -> 'None':

        os.environ[On_Prem_Gateway.Env.Admin_Port] = '21227'

        result = get_hub_admin_url()

        self.assertEqual(result, 'http://127.0.0.1:21227')

# ################################################################################################################################
# ################################################################################################################################

class TestHubClient(TestCase):
    """ The loopback API the services read and write the hub's configuration through.
    """

    def setUp(self) -> 'None':
        self.client = HubClient(_Hub_Admin_Url)

# ################################################################################################################################

    def test_get_gateways(self) -> 'None':

        gateways = [{'name': _Gateway_Name, 'is_connected': True}]
        payload = {'gateways': gateways}

        with patch('zato.server.on_prem_gateway.requests.request') as request:
            request.return_value = _get_response(OK, payload)

            result = self.client.get_gateways()

        self.assertEqual(result, gateways)

# ################################################################################################################################

    def test_put_gateways_sends_the_whole_list(self) -> 'None':

        gateways = [{'name': _Gateway_Name, 'is_active': True, 'hosts': [_Erp_Address]}]

        with patch('zato.server.on_prem_gateway.requests.request') as request:
            request.return_value = _get_response(OK, {'ok': True})

            self.client.put_gateways(gateways)

        _, kwargs = request.call_args

        self.assertEqual(kwargs['json'], {'gateways': gateways})

# ################################################################################################################################

    def test_mint_token(self) -> 'None':

        payload = {'ok': True, 'token': _Enrollment_Token, 'expires_at': '2026-09-23T10:00:00Z'}
        address = 'https://zato.example.com:11224'

        with patch('zato.server.on_prem_gateway.requests.request') as request:
            request.return_value = _get_response(OK, payload)

            result = self.client.mint_token(_Gateway_Name, address)

        self.assertEqual(result['token'], _Enrollment_Token)

        args, kwargs = request.call_args
        expected_url = f'{_Hub_Admin_Url}/gateways/{_Gateway_Name}/enrollment-token'

        self.assertEqual(args[0], 'POST')
        self.assertEqual(args[1], expected_url)
        self.assertEqual(kwargs['json'], {'address': address})

# ################################################################################################################################

    def test_a_refusal_carries_the_hub_message(self) -> 'None':

        error = f'there is no gateway called {_Other_Gateway_Name}'
        payload = {'ok': False, 'error': error}

        with patch('zato.server.on_prem_gateway.requests.request') as request:
            request.return_value = _get_response(BAD_REQUEST, payload)

            with self.assertRaises(Exception) as context:
                _ = self.client.reset_key(_Other_Gateway_Name)

        self.assertIn(error, str(context.exception))

# ################################################################################################################################

    def test_a_hub_that_is_down_is_reported_as_such(self) -> 'None':

        with patch('zato.server.on_prem_gateway.requests.request') as request:
            request.side_effect = Exception('connection refused')

            result = self.client.ping()

        self.assertFalse(result)

# ################################################################################################################################
# ################################################################################################################################

class TestManagerStatusList(TestCase):
    """ The ODB merged with whatever the hub knows.
    """

    def _get_manager(self, rows:'anylist') -> 'OnPremGatewayManager':

        server = MagicMock()
        server.cluster_id = 1

        session = MagicMock()
        out = OnPremGatewayManager(server, session=session)

        def get_list() -> 'anylist':
            return rows

        out.get_list = get_list

        return out

# ################################################################################################################################

    def _get_rows(self) -> 'strdictlist':

        out = [{'id': 1, 'name': _Gateway_Name, 'is_active': True, 'hosts': [_Erp_Address]}]

        return out

# ################################################################################################################################

    def test_live_state_is_merged_in(self) -> 'None':

        loopback = [{'host': 'erp-db.corp.local', 'address': '127.0.1.1', 'port': 5432}]

        live_state = {
            'name': _Gateway_Name,
            'is_connected': True,
            'has_key': True,
            'key_fingerprint': _Key_Fingerprint,
            'connected_since': '2026-09-22T10:00:00Z',
            'remote_address': '203.0.113.7',
            'gateway_version': '1.0.0',
            'platform': 'windows/amd64',
            'session_count': 1,
            'loopback': loopback,
        }

        manager = self._get_manager(self._get_rows())
        manager.hub = MagicMock()
        manager.hub.get_gateways.return_value = [live_state]

        result = manager.get_status_list()
        gateway_count = len(result)

        self.assertEqual(gateway_count, 1)

        gateway = result[0]

        self.assertTrue(gateway['is_connected'])
        self.assertEqual(gateway['key_fingerprint'], _Key_Fingerprint)
        self.assertEqual(gateway['host_count'], 1)
        self.assertEqual(gateway['hub_error'], '')

# ################################################################################################################################

    def test_a_hub_that_is_down_leaves_the_configuration_readable(self) -> 'None':

        manager = self._get_manager(self._get_rows())
        manager.hub = MagicMock()
        manager.hub.get_gateways.side_effect = Exception('the hub is not responding')

        result = manager.get_status_list()
        gateway_count = len(result)

        self.assertEqual(gateway_count, 1)

        gateway = result[0]

        self.assertFalse(gateway['is_connected'])
        self.assertFalse(gateway['has_key'])
        self.assertEqual(gateway['hosts'], [_Erp_Address])
        self.assertIn('the hub is not responding', gateway['hub_error'])

# ################################################################################################################################

    def test_sync_pushes_only_the_declarative_half(self) -> 'None':

        manager = self._get_manager(self._get_rows())
        manager.hub = MagicMock()

        manager.sync()

        expected = [{
            'name': _Gateway_Name,
            'is_active': True,
            'hosts': [_Erp_Address],
        }]

        manager.hub.put_gateways.assert_called_once_with(expected)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
