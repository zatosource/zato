# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.bunch import Bunch
from zato.common.json_internal import dumps
from zato.common.rate_limiting.common import Window_Unit_Second
from zato.common.rate_limiting.manager import RateLimitingManager
from zato.server.base.parallel.config import ConfigLoader
from zato.server.config import ConfigDict

# ################################################################################################################################
# ################################################################################################################################

def _all_day_range(**overrides):
    out = {
        'is_all_day':  True,
        'disabled':    False,
        'disallowed':  False,
        'rate':        100,
        'burst':       200,
        'limit':       1000,
        'limit_unit':  Window_Unit_Second,
    }
    out.update(overrides)
    return out

# ################################################################################################################################

def _make_rule(cidr_list, time_range):
    return {
        'cidr_list': cidr_list,
        'time_range': time_range,
    }

# ################################################################################################################################
# ################################################################################################################################

class StartupLoadingTestCase(unittest.TestCase):

    def test_channels_with_rate_limiting_are_loaded(self):
        """ On startup, channels that have rate_limiting in their opaque data
        get their config loaded into the manager.
        """
        manager = RateLimitingManager()

        rules = [_make_rule(['10.0.0.0/8'], [_all_day_range()])]

        http_soap = [
            {'id': 1, 'name': 'ch1', 'rate_limiting': rules},
            {'id': 2, 'name': 'ch2'},
            {'id': 3, 'name': 'ch3', 'rate_limiting': [_make_rule(['192.168.0.0/16'], [_all_day_range(rate=50)])]},
        ]

        for hs_item in http_soap:
            rate_limiting = hs_item.get('rate_limiting')
            if rate_limiting:
                channel_id = hs_item['id']
                manager.set_channel_config(channel_id, rate_limiting)

        self.assertTrue(manager.has_channel(1))
        self.assertFalse(manager.has_channel(2))
        self.assertTrue(manager.has_channel(3))

    def test_channels_without_rate_limiting_are_skipped(self):
        """ Channels that have no rate_limiting key are not registered.
        """
        manager = RateLimitingManager()

        http_soap = [
            {'id': 1, 'name': 'ch1'},
            {'id': 2, 'name': 'ch2'},
        ]

        for hs_item in http_soap:
            rate_limiting = hs_item.get('rate_limiting')
            if rate_limiting:
                channel_id = hs_item['id']
                manager.set_channel_config(channel_id, rate_limiting)

        self.assertFalse(manager.has_channel(1))
        self.assertFalse(manager.has_channel(2))

# ################################################################################################################################
# ################################################################################################################################

def _make_config_dict(name, entries):
    """ Builds a ConfigDict with the given entries, each a dict with 'id', 'name', and optionally 'opaque1'.
    """
    config_dict = ConfigDict(name, Bunch())

    for entry in entries:
        entry_name = entry['name']
        config_dict._impl[entry_name] = {'config': entry}

    return config_dict

# ################################################################################################################################

def _make_loader(manager):
    """ Builds a minimal object that has _load_sec_def_rate_limiting bound.
    """
    loader = object.__new__(ConfigLoader)
    loader.rate_limiting_manager = manager
    return loader

# ################################################################################################################################
# ################################################################################################################################

class SecDefStartupLoadingTestCase(unittest.TestCase):

    def test_basic_auth_with_rate_limiting_loaded(self):
        """ Security definitions with rate_limiting in opaque1 are loaded.
        """
        manager = RateLimitingManager()
        loader = _make_loader(manager)

        rules = [_make_rule(['10.0.0.0/8'], [_all_day_range()])]
        opaque = dumps({'rate_limiting': rules})

        config_dict = _make_config_dict('basic_auth', [
            {'id': 10, 'name': 'my-basic-auth', 'opaque1': opaque},
        ])

        loader._load_sec_def_rate_limiting(config_dict)

        self.assertTrue(manager.has_sec_def(10))

    def test_sec_def_without_opaque_skipped(self):
        """ Security definitions with no opaque1 are not registered.
        """
        manager = RateLimitingManager()
        loader = _make_loader(manager)

        config_dict = _make_config_dict('basic_auth', [
            {'id': 11, 'name': 'no-opaque'},
        ])

        loader._load_sec_def_rate_limiting(config_dict)

        self.assertFalse(manager.has_sec_def(11))

    def test_sec_def_with_empty_opaque_skipped(self):
        """ Security definitions with opaque1 as None are not registered.
        """
        manager = RateLimitingManager()
        loader = _make_loader(manager)

        config_dict = _make_config_dict('apikey', [
            {'id': 12, 'name': 'empty-opaque', 'opaque1': None},
        ])

        loader._load_sec_def_rate_limiting(config_dict)

        self.assertFalse(manager.has_sec_def(12))

    def test_sec_def_with_opaque_but_no_rate_limiting_skipped(self):
        """ Security definitions whose opaque1 has no rate_limiting key are not registered.
        """
        manager = RateLimitingManager()
        loader = _make_loader(manager)

        opaque = dumps({'header': 'X-API-Key'})

        config_dict = _make_config_dict('apikey', [
            {'id': 13, 'name': 'no-rl-key', 'opaque1': opaque},
        ])

        loader._load_sec_def_rate_limiting(config_dict)

        self.assertFalse(manager.has_sec_def(13))

    def test_multiple_sec_defs_mixed(self):
        """ Only entries with rate_limiting in opaque1 are loaded.
        """
        manager = RateLimitingManager()
        loader = _make_loader(manager)

        rules = [_make_rule(['172.16.0.0/12'], [_all_day_range()])]
        opaque_with_rl = dumps({'rate_limiting': rules})
        opaque_without_rl = dumps({'header': 'X-API-Key'})

        config_dict = _make_config_dict('apikey', [
            {'id': 20, 'name': 'with-rl', 'opaque1': opaque_with_rl},
            {'id': 21, 'name': 'without-rl', 'opaque1': opaque_without_rl},
            {'id': 22, 'name': 'no-opaque'},
        ])

        loader._load_sec_def_rate_limiting(config_dict)

        self.assertTrue(manager.has_sec_def(20))
        self.assertFalse(manager.has_sec_def(21))
        self.assertFalse(manager.has_sec_def(22))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
