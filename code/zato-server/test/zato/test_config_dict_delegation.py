# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

"""
Tests for ConfigDict delegation to the Rust ConfigStore.
Verifies that the delegating ConfigDict behaves identically
to the old Bunch-backed one from Python's perspective.
"""

# stdlib
import unittest

# Zato
from zato_server_core import ConfigStore
from zato.server.config import ConfigDict

# ################################################################################################################################
# ################################################################################################################################

class TestConfigDictDelegation(unittest.TestCase):

    def setUp(self):
        self.cs = ConfigStore()
        self.cs.set('channel_rest', 'ch1', {
            'name': 'ch1', 'url_path': '/ch1', 'service': 'svc1',
        })
        self.cs.set('channel_rest', 'ch2', {
            'name': 'ch2', 'url_path': '/ch2', 'service': 'svc2',
        })
        self.cd = ConfigDict('channel_rest', config_store=self.cs, entity_type='channel_rest')

    def test_get_returns_bunch_wrapper(self):
        item = self.cd.get('ch1')
        self.assertIsNotNone(item)
        self.assertIn('config', item)
        self.assertEqual(item['config']['service'], 'svc1')
        self.assertEqual(item.config.service, 'svc1')

    def test_get_nonexistent_returns_default(self):
        self.assertIsNone(self.cd.get('nope'))
        self.assertEqual(self.cd.get('nope', 'fallback'), 'fallback')

    def test_getitem_returns_bunch_wrapper(self):
        item = self.cd['ch1']
        self.assertEqual(item.config.url_path, '/ch1')

    def test_getitem_raises_keyerror(self):
        with self.assertRaises(KeyError):
            _ = self.cd['nope']

    def test_keys(self):
        keys = sorted(self.cd.keys())
        self.assertEqual(keys, ['ch1', 'ch2'])

    def test_values(self):
        vals = list(self.cd.values())
        self.assertEqual(len(vals), 2)
        services = sorted(v.config.service for v in vals)
        self.assertEqual(services, ['svc1', 'svc2'])

    def test_items(self):
        items = dict(self.cd.items())
        self.assertIn('ch1', items)
        self.assertIn('ch2', items)
        self.assertEqual(items['ch1'].config.service, 'svc1')

    def test_iter(self):
        names = sorted(self.cd)
        self.assertEqual(names, ['ch1', 'ch2'])

    def test_set_writes_to_rust(self):
        from zato.bunch import Bunch
        self.cd.set('ch3', Bunch({'config': Bunch({
            'name': 'ch3', 'url_path': '/ch3', 'service': 'svc3',
        })}))
        raw = self.cs.get('channel_rest', 'ch3')
        self.assertIsNotNone(raw)
        self.assertEqual(raw['service'], 'svc3')

    def test_delitem_removes_from_rust(self):
        del self.cd['ch1']
        self.assertIsNone(self.cs.get('channel_rest', 'ch1'))
        self.assertIsNone(self.cd.get('ch1'))

    def test_mutation_in_rust_visible_immediately(self):
        self.cs.set('channel_rest', 'ch1', {
            'name': 'ch1', 'url_path': '/ch1', 'service': 'new-svc',
        })
        item = self.cd.get('ch1')
        self.assertEqual(item.config.service, 'new-svc')

    def test_delete_in_rust_visible_immediately(self):
        self.cs.delete('channel_rest', 'ch1')
        self.assertIsNone(self.cd.get('ch1'))

    def test_get_config_list(self):
        configs = self.cd.get_config_list()
        self.assertEqual(len(configs), 2)
        services = sorted(c.service for c in configs)
        self.assertEqual(services, ['svc1', 'svc2'])

    def test_copy_keys(self):
        keys = sorted(self.cd.copy_keys())
        self.assertEqual(keys, ['ch1', 'ch2'])

    def test_copy_returns_delegating_instance(self):
        cd2 = self.cd.copy()
        item = cd2.get('ch1')
        self.assertIsNotNone(item)
        self.assertEqual(item.config.service, 'svc1')

    def test_pop(self):
        item = self.cd.pop('ch1', None)
        self.assertIsNotNone(item)
        self.assertEqual(item.config.service, 'svc1')
        self.assertIsNone(self.cd.get('ch1'))

    def test_pop_nonexistent(self):
        result = self.cd.pop('nope', 'default')
        self.assertEqual(result, 'default')

# ################################################################################################################################
# ################################################################################################################################

class TestConfigDictSecurityFilter(unittest.TestCase):

    def setUp(self):
        self.cs = ConfigStore()
        self.cs.set('security', 'ba1', {
            'type': 'basic_auth', 'name': 'ba1', 'username': 'u1', 'password': 'p1',
        })
        self.cs.set('security', 'ak1', {
            'type': 'apikey', 'name': 'ak1', 'username': 'u2', 'password': 'p2',
        })

    def test_basic_auth_filter(self):
        cd = ConfigDict('basic_auth', config_store=self.cs, entity_type='security', sec_type_filter='basic_auth')
        self.assertIsNotNone(cd.get('ba1'))
        self.assertIsNone(cd.get('ak1'))
        self.assertEqual(len(list(cd.keys())), 1)

    def test_apikey_filter(self):
        cd = ConfigDict('apikey', config_store=self.cs, entity_type='security', sec_type_filter='apikey')
        self.assertIsNotNone(cd.get('ak1'))
        self.assertIsNone(cd.get('ba1'))
        self.assertEqual(len(list(cd.keys())), 1)

# ################################################################################################################################
# ################################################################################################################################

class TestConfigDictLegacyMode(unittest.TestCase):
    """Verify that ConfigDict still works with a Bunch when no config_store is given."""

    def setUp(self):
        from zato.bunch import Bunch
        impl = Bunch()
        impl['ch1'] = Bunch({'config': Bunch({'name': 'ch1', 'service': 'svc1'})})
        self.cd = ConfigDict('test', impl)

    def test_get(self):
        item = self.cd.get('ch1')
        self.assertEqual(item.config.service, 'svc1')

    def test_set(self):
        from zato.bunch import Bunch
        self.cd.set('ch2', Bunch({'config': Bunch({'name': 'ch2', 'service': 'svc2'})}))
        self.assertIsNotNone(self.cd.get('ch2'))

    def test_keys(self):
        self.assertEqual(list(self.cd.keys()), ['ch1'])

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
