# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock

# Zato
from zato.common.json_internal import dumps
from zato.common.rate_limiting.common import Window_Unit_Second
from zato.server.service.internal.http_soap import RateLimitingGet

# ################################################################################################################################
# ################################################################################################################################

def _make_service(channel_id, existing_opaque=None):
    """ Builds a bare object with just enough state for handle() to work.
    """
    service = object.__new__(RateLimitingGet)

    service.request = MagicMock()
    service.request.input = {'id': str(channel_id)}

    service.response = MagicMock()

    mock_item = type('MockItem', (), {
        'opaque1': dumps(existing_opaque) if existing_opaque is not None else None,
    })()

    mock_session = MagicMock()
    mock_session.query.return_value.filter_by.return_value.one.return_value = mock_item

    service.odb = MagicMock()
    service.odb.session.return_value = mock_session

    return service

# ################################################################################################################################
# ################################################################################################################################

class RateLimitingGetTestCase(unittest.TestCase):

    def test_returns_empty_list_when_no_rules(self):
        """ When opaque1 is None, an empty list is returned.
        """
        service = _make_service(42, existing_opaque=None)

        service.handle()

        self.assertEqual(service.response.payload['rate_limiting'], [])

    def test_returns_empty_list_when_no_rate_limiting_key(self):
        """ When opaque1 exists but has no rate_limiting key, an empty list is returned.
        """
        service = _make_service(42, existing_opaque={'http_accept': 'text/html'})

        service.handle()

        self.assertEqual(service.response.payload['rate_limiting'], [])

    def test_returns_stored_rules_verbatim(self):
        """ When rate_limiting rules exist, they are returned as-is.
        """
        rules = [
            {
                'cidr_list': ['10.0.0.0/8'],
                'time_range': [{
                    'is_all_day': True,
                    'disabled': False,
                    'disallowed': False,
                    'rate': 100,
                    'burst': 200,
                    'limit': 1000,
                    'limit_unit': Window_Unit_Second,
                }],
            },
        ]
        service = _make_service(42, existing_opaque={'rate_limiting': rules})

        service.handle()

        self.assertEqual(service.response.payload['rate_limiting'], rules)

    def test_returns_multiple_rules(self):
        """ Multiple rules are all returned.
        """
        rules = [
            {
                'cidr_list': ['10.0.0.0/8'],
                'time_range': [{
                    'is_all_day': True,
                    'disabled': False,
                    'disallowed': False,
                    'rate': 100,
                    'burst': 200,
                    'limit': 1000,
                    'limit_unit': Window_Unit_Second,
                }],
            },
            {
                'cidr_list': ['192.168.0.0/16'],
                'time_range': [{
                    'is_all_day': True,
                    'disabled': False,
                    'disallowed': False,
                    'rate': 50,
                    'burst': 100,
                    'limit': 500,
                    'limit_unit': Window_Unit_Second,
                }],
            },
        ]
        service = _make_service(42, existing_opaque={'rate_limiting': rules})

        service.handle()

        result = service.response.payload['rate_limiting']
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['cidr_list'], ['10.0.0.0/8'])
        self.assertEqual(result[1]['cidr_list'], ['192.168.0.0/16'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
