# -*- coding: utf-8 -*-

"""
Tests for the Rust-backed ConfigStore.
"""

# stdlib
import os
import tempfile
import unittest

# Zato
from zato_server_core import ConfigStore

# ################################################################################################################################

class TestConfigStoreLoadYAML(unittest.TestCase):

    yaml_full = '''
security:
  - type: basic_auth
    name: test-ba
    username: admin
    password: secret
    realm: myrealm
  - type: apikey
    name: test-ak
    username: keyuser

groups:
  - name: grp1
    members: [test-ba, test-ak]

channel_rest:
  - name: /api/v1
    url_path: /api/v1
    service: my.service
    method: POST

outgoing_rest:
  - name: ext-crm
    host: https://crm.example.com
    url_path: /v2
    timeout: 30

scheduler:
  - name: daily-cleanup
    service: cleanup.old
    job_type: interval_based
    hours: 24

cache:
  - name: default
    is_default: true
    max_size: 5000

email_smtp:
  - name: notifier
    host: smtp.example.com
    port: 587

email_imap:
  - name: inbox
    host: imap.example.com
    port: 993

zato_generic_connection:
  - name: my-ldap
    type_: outconn-ldap
    address: ldap://10.0.0.5
    port: 389
    opaque:
      auth_type: simple

pubsub_topic:
  - name: /events/order
    is_active: true

elastic_search:
  - name: main-es
    hosts: http://es:9200
    timeout: 15
'''

    def setUp(self):
        self.cs = ConfigStore()
        self.cs.load_yaml_string(self.yaml_full)

    def test_security_count(self):
        self.assertEqual(len(self.cs.get_list('security')), 2)

    def test_security_get_by_name(self):
        item = self.cs.get('security', 'test-ba')
        self.assertIsNotNone(item)
        self.assertEqual(item['username'], 'admin')
        self.assertEqual(item['realm'], 'myrealm')

    def test_security_missing(self):
        self.assertIsNone(self.cs.get('security', 'nonexistent'))

    def test_groups(self):
        grp = self.cs.get('groups', 'grp1')
        self.assertIsNotNone(grp)
        self.assertEqual(sorted(grp['members']), ['test-ak', 'test-ba'])

    def test_channel_rest(self):
        items = self.cs.get_list('channel_rest')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['service'], 'my.service')

    def test_outgoing_rest(self):
        items = self.cs.get_list('outgoing_rest')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['host'], 'https://crm.example.com')

    def test_scheduler(self):
        items = self.cs.get_list('scheduler')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['name'], 'daily-cleanup')
        self.assertEqual(items[0]['hours'], 24)

    def test_cache(self):
        items = self.cs.get_list('cache_builtin')
        self.assertEqual(len(items), 1)
        self.assertTrue(items[0]['is_default'])

    def test_email_smtp(self):
        items = self.cs.get_list('email_smtp')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['port'], 587)

    def test_email_imap(self):
        items = self.cs.get_list('email_imap')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['port'], 993)

    def test_generic_connection(self):
        items = self.cs.get_list('generic_connection')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['type_'], 'outconn-ldap')
        self.assertEqual(items[0]['opaque']['auth_type'], 'simple')

    def test_pubsub_topic(self):
        items = self.cs.get_list('pubsub_topic')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['name'], '/events/order')

    def test_elastic_search(self):
        items = self.cs.get_list('elastic_search')
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['timeout'], 15)

# ################################################################################################################################

class TestConfigStoreCRUD(unittest.TestCase):

    def setUp(self):
        self.cs = ConfigStore()

    def test_set_get(self):
        self.cs.set('channel_rest', 'ch1', {'name': 'ch1', 'url_path': '/ch1', 'service': 'svc1'})
        item = self.cs.get('channel_rest', 'ch1')
        self.assertIsNotNone(item)
        self.assertEqual(item['service'], 'svc1')

    def test_set_overwrite(self):
        self.cs.set('channel_rest', 'ch1', {'name': 'ch1', 'url_path': '/ch1', 'service': 'svc1'})
        self.cs.set('channel_rest', 'ch1', {'name': 'ch1', 'url_path': '/ch1', 'service': 'svc2'})
        item = self.cs.get('channel_rest', 'ch1')
        self.assertEqual(item['service'], 'svc2')

    def test_delete(self):
        self.cs.set('channel_rest', 'ch1', {'name': 'ch1', 'url_path': '/ch1', 'service': 'svc1'})
        deleted = self.cs.delete('channel_rest', 'ch1')
        self.assertTrue(deleted)
        self.assertIsNone(self.cs.get('channel_rest', 'ch1'))

    def test_delete_nonexistent(self):
        deleted = self.cs.delete('channel_rest', 'nope')
        self.assertFalse(deleted)

    def test_get_list_empty(self):
        items = self.cs.get_list('channel_rest')
        self.assertEqual(len(items), 0)

    def test_get_list_multiple(self):
        for i in range(5):
            name = f'ch{i}'
            self.cs.set('channel_rest', name, {'name': name, 'url_path': f'/{name}', 'service': f'svc{i}'})
        items = self.cs.get_list('channel_rest')
        self.assertEqual(len(items), 5)

    def test_unknown_entity_type(self):
        with self.assertRaises(ValueError):
            self.cs.get('nonexistent_type', 'foo')

    def test_security_tagged_enum(self):
        self.cs.set('security', 'my-auth', {
            'type': 'basic_auth',
            'name': 'my-auth',
            'username': 'admin',
            'password': 'pass',
        })
        item = self.cs.get('security', 'my-auth')
        self.assertIsNotNone(item)
        self.assertEqual(item['sec_type'], 'basic_auth')

# ################################################################################################################################

class TestConfigStoreLoadFile(unittest.TestCase):

    def test_load_from_file(self):
        yaml_content = '''
channel_rest:
  - name: file-ch
    url_path: /from-file
    service: file.service
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            path = f.name

        try:
            cs = ConfigStore()
            cs.load_yaml(path)
            items = cs.get_list('channel_rest')
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]['name'], 'file-ch')
        finally:
            os.unlink(path)

    def test_load_nonexistent_file(self):
        cs = ConfigStore()
        with self.assertRaises(OSError):
            cs.load_yaml('/nonexistent/path.yaml')

    def test_load_invalid_yaml(self):
        cs = ConfigStore()
        with self.assertRaises(ValueError):
            cs.load_yaml_string('{{{invalid yaml:::')

# ################################################################################################################################

class TestConfigStoreExport(unittest.TestCase):

    def test_export_round_trip(self):
        cs = ConfigStore()
        yaml_in = '''
security:
  - type: basic_auth
    name: ba1
    username: user1

channel_rest:
  - name: ch1
    url_path: /ch1
    service: svc1

scheduler:
  - name: job1
    service: job.svc
    job_type: interval_based
    minutes: 10
'''
        cs.load_yaml_string(yaml_in)
        exported = cs.export_to_dict()

        self.assertIn('security', exported)
        self.assertIn('channel_rest', exported)
        self.assertIn('scheduler', exported)

        self.assertEqual(len(exported['security']), 1)
        self.assertEqual(len(exported['channel_rest']), 1)
        self.assertEqual(len(exported['scheduler']), 1)

    def test_export_empty(self):
        cs = ConfigStore()
        exported = cs.export_to_dict()
        self.assertEqual(len(exported), 0)

# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
