# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest
from unittest.mock import MagicMock

# Bunch
from bunch import Bunch

# Zato
from zato.common.rate_limiting.common import Window_Unit_Second
from zato.server.base.config_manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

def _make_config_manager():
    """ Builds a minimal ConfigManager with a mocked server that has a rate_limiting_manager.
    """
    server = MagicMock()
    server.rate_limiting_manager = MagicMock()

    config_manager = object.__new__(ConfigManager)
    config_manager.server = server

    return config_manager

# ################################################################################################################################
# ################################################################################################################################

class ConfigManagerRateLimitingTestCase(unittest.TestCase):

    def test_handler_calls_set_channel_config(self):
        """ The handler passes channel_id and rule_dicts to the manager.
        """
        config_manager = _make_config_manager()

        rule_dicts = [
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

        msg = Bunch({
            'id': 42,
            'rule_dicts': rule_dicts,
        })

        config_manager.on_config_event_CHANNEL_HTTP_SOAP_RATE_LIMITING_EDIT(msg)

        config_manager.server.rate_limiting_manager.set_channel_config.assert_called_once_with(42, rule_dicts)

    def test_handler_with_empty_rules(self):
        """ An empty rule_dicts list is passed through to the manager.
        """
        config_manager = _make_config_manager()

        msg = Bunch({
            'id': 7,
            'rule_dicts': [],
        })

        config_manager.on_config_event_CHANNEL_HTTP_SOAP_RATE_LIMITING_EDIT(msg)

        config_manager.server.rate_limiting_manager.set_channel_config.assert_called_once_with(7, [])

# ################################################################################################################################
# ################################################################################################################################

class ConfigManagerBasicAuthRateLimitingTestCase(unittest.TestCase):

    def test_handler_calls_set_sec_def_config(self):
        """ The handler passes sec_def_id and rule_dicts to the manager.
        """
        config_manager = _make_config_manager()

        rule_dicts = [
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

        msg = Bunch({
            'id': 10,
            'rule_dicts': rule_dicts,
        })

        config_manager.on_config_event_SECURITY_BASIC_AUTH_RATE_LIMITING_EDIT(msg)

        config_manager.server.rate_limiting_manager.set_sec_def_config.assert_called_once_with(10, rule_dicts)

    def test_handler_with_empty_rules(self):
        """ An empty rule_dicts list is passed through to the manager.
        """
        config_manager = _make_config_manager()

        msg = Bunch({
            'id': 15,
            'rule_dicts': [],
        })

        config_manager.on_config_event_SECURITY_BASIC_AUTH_RATE_LIMITING_EDIT(msg)

        config_manager.server.rate_limiting_manager.set_sec_def_config.assert_called_once_with(15, [])

# ################################################################################################################################
# ################################################################################################################################

class ConfigManagerAPIKeyRateLimitingTestCase(unittest.TestCase):

    def test_handler_calls_set_sec_def_config(self):
        """ The handler passes sec_def_id and rule_dicts to the manager.
        """
        config_manager = _make_config_manager()

        rule_dicts = [
            {
                'cidr_list': ['172.16.0.0/12'],
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

        msg = Bunch({
            'id': 20,
            'rule_dicts': rule_dicts,
        })

        config_manager.on_config_event_SECURITY_APIKEY_RATE_LIMITING_EDIT(msg)

        config_manager.server.rate_limiting_manager.set_sec_def_config.assert_called_once_with(20, rule_dicts)

    def test_handler_with_empty_rules(self):
        """ An empty rule_dicts list is passed through to the manager.
        """
        config_manager = _make_config_manager()

        msg = Bunch({
            'id': 25,
            'rule_dicts': [],
        })

        config_manager.on_config_event_SECURITY_APIKEY_RATE_LIMITING_EDIT(msg)

        config_manager.server.rate_limiting_manager.set_sec_def_config.assert_called_once_with(25, [])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
