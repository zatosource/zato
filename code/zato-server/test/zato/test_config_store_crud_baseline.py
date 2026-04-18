# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

"""
Baseline tests for the ConfigManager CRUD cycle.

These tests exercise create, read, edit, rename, delete
for every entity type. They must pass before any refactoring
begins and must continue to pass after every subsequent phase.
"""

# stdlib
import unittest

# Zato
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

class CRUDTestMixin:
    """Mixin providing reusable CRUD test patterns for any entity type.
    Not discovered by unittest because it does not inherit from TestCase."""

    entity_type = None
    sample_data = None
    edit_field = None
    edit_value_before = None
    edit_value_after = None

    def setUp(self):
        self.cm = ConfigManager()

    def _name(self):
        return self.sample_data['name']

    def test_create_and_get(self):
        self.cm.set(self.entity_type, self._name(), self.sample_data)
        item = self.cm.get(self.entity_type, self._name())
        self.assertIsNotNone(item)
        self.assertEqual(item['name'], self._name())

    def test_create_and_get_list(self):
        self.cm.set(self.entity_type, self._name(), self.sample_data)
        items = self.cm.get_list(self.entity_type)
        self.assertEqual(len(items), 1)

    def test_get_nonexistent(self):
        self.assertIsNone(self.cm.get(self.entity_type, 'does-not-exist'))

    def test_get_list_empty(self):
        items = self.cm.get_list(self.entity_type)
        self.assertEqual(len(items), 0)

    def test_edit_field(self):
        self.cm.set(self.entity_type, self._name(), self.sample_data)
        item = self.cm.get(self.entity_type, self._name())
        self.assertEqual(item[self.edit_field], self.edit_value_before)

        updated = dict(self.sample_data)
        updated[self.edit_field] = self.edit_value_after
        self.cm.set(self.entity_type, self._name(), updated)

        item = self.cm.get(self.entity_type, self._name())
        self.assertEqual(item[self.edit_field], self.edit_value_after)
        self.assertEqual(item['name'], self._name())

    def test_rename(self):
        self.cm.set(self.entity_type, self._name(), self.sample_data)
        self.cm.delete(self.entity_type, self._name())

        new_name = self._name() + '-renamed'
        renamed_data = dict(self.sample_data)
        renamed_data['name'] = new_name
        self.cm.set(self.entity_type, new_name, renamed_data)

        self.assertIsNone(self.cm.get(self.entity_type, self._name()))
        item = self.cm.get(self.entity_type, new_name)
        self.assertIsNotNone(item)
        self.assertEqual(item['name'], new_name)

    def test_delete(self):
        self.cm.set(self.entity_type, self._name(), self.sample_data)
        deleted = self.cm.delete(self.entity_type, self._name())
        self.assertTrue(deleted)
        self.assertIsNone(self.cm.get(self.entity_type, self._name()))

    def test_delete_nonexistent(self):
        deleted = self.cm.delete(self.entity_type, 'does-not-exist')
        self.assertFalse(deleted)

    def test_overwrite(self):
        self.cm.set(self.entity_type, self._name(), self.sample_data)
        updated = dict(self.sample_data)
        updated[self.edit_field] = self.edit_value_after
        self.cm.set(self.entity_type, self._name(), updated)
        item = self.cm.get(self.entity_type, self._name())
        self.assertEqual(item[self.edit_field], self.edit_value_after)

    def test_multiple_items(self):
        for i in range(5):
            data = dict(self.sample_data)
            data['name'] = f'{self._name()}-{i}'
            self.cm.set(self.entity_type, data['name'], data)
        items = self.cm.get_list(self.entity_type)
        self.assertEqual(len(items), 5)

    def test_get_list_after_delete(self):
        for i in range(3):
            data = dict(self.sample_data)
            data['name'] = f'{self._name()}-{i}'
            self.cm.set(self.entity_type, data['name'], data)
        self.cm.delete(self.entity_type, f'{self._name()}-1')
        items = self.cm.get_list(self.entity_type)
        self.assertEqual(len(items), 2)

# ################################################################################################################################
# Security types
# ################################################################################################################################

class TestCRUDBasicAuth(CRUDTestMixin, unittest.TestCase):
    entity_type = 'security'
    sample_data = {
        'type': 'basic_auth',
        'name': 'test-basic-auth',
        'username': 'admin',
        'password': 'secret123',
        'realm': 'myrealm',
    }
    edit_field = 'username'
    edit_value_before = 'admin'
    edit_value_after = 'newadmin'

    def test_all_fields_roundtrip(self):
        self.cm.set(self.entity_type, self._name(), self.sample_data)
        item = self.cm.get(self.entity_type, self._name())
        self.assertEqual(item['username'], 'admin')
        self.assertEqual(item['password'], 'secret123')
        self.assertEqual(item['realm'], 'myrealm')

# ################################################################################################################################

class TestCRUDApiKey(CRUDTestMixin, unittest.TestCase):
    entity_type = 'security'
    sample_data = {
        'type': 'apikey',
        'name': 'test-apikey',
        'username': 'keyuser',
        'password': 'key-value-123',
    }
    edit_field = 'username'
    edit_value_before = 'keyuser'
    edit_value_after = 'newkeyuser'

# ################################################################################################################################

class TestCRUDNtlm(CRUDTestMixin, unittest.TestCase):
    entity_type = 'security'
    sample_data = {
        'type': 'ntlm',
        'name': 'test-ntlm',
        'username': 'domain\\user',
        'password': 'ntlm-pass',
    }
    edit_field = 'username'
    edit_value_before = 'domain\\user'
    edit_value_after = 'domain\\newuser'

# ################################################################################################################################

class TestCRUDBearerToken(CRUDTestMixin, unittest.TestCase):
    entity_type = 'security'
    sample_data = {
        'type': 'bearer_token',
        'name': 'test-bearer',
        'username': 'bearer-user',
        'password': 'bearer-secret',
        'auth_endpoint': 'https://auth.example.com/token',
        'client_id_field': 'client_id',
        'client_secret_field': 'client_secret',
        'grant_type': 'client_credentials',
        'data_format': 'json',
    }
    edit_field = 'auth_endpoint'
    edit_value_before = 'https://auth.example.com/token'
    edit_value_after = 'https://auth2.example.com/token'

# ################################################################################################################################
# Channel types
# ################################################################################################################################

class TestCRUDChannelRest(CRUDTestMixin, unittest.TestCase):
    entity_type = 'channel_rest'
    sample_data = {
        'name': '/api/test',
        'url_path': '/api/test',
        'service': 'my.test.service',
        'method': 'POST',
    }
    edit_field = 'service'
    edit_value_before = 'my.test.service'
    edit_value_after = 'my.new.service'

# ################################################################################################################################

class TestCRUDChannelSoap(CRUDTestMixin, unittest.TestCase):
    entity_type = 'channel_soap'
    sample_data = {
        'name': 'soap-channel',
        'url_path': '/soap/v1',
        'service': 'soap.service',
        'soap_action': 'urn:test',
    }
    edit_field = 'service'
    edit_value_before = 'soap.service'
    edit_value_after = 'soap.new.service'

# ################################################################################################################################

class TestCRUDChannelAmqp(CRUDTestMixin, unittest.TestCase):
    entity_type = 'channel_amqp'
    sample_data = {
        'name': 'amqp-channel',
        'address': 'amqp://localhost',
        'username': 'guest',
        'password': 'guest',
        'queue': 'test-queue',
        'service': 'amqp.service',
    }
    edit_field = 'queue'
    edit_value_before = 'test-queue'
    edit_value_after = 'new-queue'

# ################################################################################################################################
# Outgoing types
# ################################################################################################################################

class TestCRUDOutgoingRest(CRUDTestMixin, unittest.TestCase):
    entity_type = 'outgoing_rest'
    sample_data = {
        'name': 'ext-api',
        'host': 'https://api.example.com',
        'url_path': '/v2',
        'timeout': 30,
    }
    edit_field = 'host'
    edit_value_before = 'https://api.example.com'
    edit_value_after = 'https://api2.example.com'

# ################################################################################################################################

class TestCRUDOutgoingSoap(CRUDTestMixin, unittest.TestCase):
    entity_type = 'outgoing_soap'
    sample_data = {
        'name': 'ext-soap',
        'host': 'https://soap.example.com',
        'url_path': '/ws',
        'soap_action': 'urn:process',
        'timeout': 60,
    }
    edit_field = 'host'
    edit_value_before = 'https://soap.example.com'
    edit_value_after = 'https://soap2.example.com'

# ################################################################################################################################

class TestCRUDOutgoingAmqp(CRUDTestMixin, unittest.TestCase):
    entity_type = 'outgoing_amqp'
    sample_data = {
        'name': 'ext-amqp',
        'address': 'amqp://broker.example.com',
        'username': 'producer',
        'password': 'prod-pass',
    }
    edit_field = 'username'
    edit_value_before = 'producer'
    edit_value_after = 'new-producer'

# ################################################################################################################################

class TestCRUDOutgoingFtp(CRUDTestMixin, unittest.TestCase):
    entity_type = 'outgoing_ftp'
    sample_data = {
        'name': 'ext-ftp',
        'host': 'ftp.example.com',
        'port': 21,
    }
    edit_field = 'host'
    edit_value_before = 'ftp.example.com'
    edit_value_after = 'ftp2.example.com'

# ################################################################################################################################

class TestCRUDSql(CRUDTestMixin, unittest.TestCase):
    entity_type = 'sql'
    sample_data = {
        'name': 'main-db',
        'host': 'db.example.com',
        'port': 5432,
        'db_name': 'mydb',
        'username': 'dbuser',
        'password': 'dbpass',
        'engine': 'postgresql',
    }
    edit_field = 'db_name'
    edit_value_before = 'mydb'
    edit_value_after = 'newdb'

# ################################################################################################################################

class TestCRUDOdoo(CRUDTestMixin, unittest.TestCase):
    entity_type = 'odoo'
    sample_data = {
        'name': 'ext-odoo',
        'host': 'odoo.example.com',
        'port': 8069,
        'user': 'admin',
        'database': 'odoo_db',
        'protocol': 'jsonrpc',
        'password': 'odoo-pass',
    }
    edit_field = 'database'
    edit_value_before = 'odoo_db'
    edit_value_after = 'new_odoo_db'

# ################################################################################################################################

class TestCRUDOutgoingSap(CRUDTestMixin, unittest.TestCase):
    entity_type = 'outgoing_sap'
    sample_data = {
        'name': 'ext-sap',
        'host': 'sap.example.com',
        'user': 'sapuser',
        'client': 'client100',
        'sysid': 'PRD',
        'password': 'sap-pass',
    }
    edit_field = 'user'
    edit_value_before = 'sapuser'
    edit_value_after = 'newsapuser'

# ################################################################################################################################
# Email types
# ################################################################################################################################

class TestCRUDEmailSmtp(CRUDTestMixin, unittest.TestCase):
    entity_type = 'email_smtp'
    sample_data = {
        'name': 'notifier',
        'host': 'smtp.example.com',
        'port': 587,
        'timeout': 30,
        'mode': 'starttls',
        'ping_address': 'test@example.com',
    }
    edit_field = 'host'
    edit_value_before = 'smtp.example.com'
    edit_value_after = 'smtp2.example.com'

# ################################################################################################################################

class TestCRUDEmailImap(CRUDTestMixin, unittest.TestCase):
    entity_type = 'email_imap'
    sample_data = {
        'name': 'inbox',
        'host': 'imap.example.com',
        'port': 993,
        'timeout': 30,
        'mode': 'ssl',
        'get_criteria': 'UNSEEN',
    }
    edit_field = 'host'
    edit_value_before = 'imap.example.com'
    edit_value_after = 'imap2.example.com'

# ################################################################################################################################
# Cache
# ################################################################################################################################

class TestCRUDCache(CRUDTestMixin, unittest.TestCase):
    entity_type = 'cache'
    sample_data = {
        'name': 'default-cache',
        'is_default': True,
        'max_size': 10000,
        'max_item_size': 1000,
        'extend_expiry_on_get': True,
        'extend_expiry_on_set': False,
    }
    edit_field = 'max_size'
    edit_value_before = 10000
    edit_value_after = 20000

# ################################################################################################################################
# Search
# ################################################################################################################################

class TestCRUDElasticSearch(CRUDTestMixin, unittest.TestCase):
    entity_type = 'elastic_search'
    sample_data = {
        'name': 'main-es',
        'hosts': 'http://es:9200',
        'timeout': 15,
        'body_as': 'json',
    }
    edit_field = 'hosts'
    edit_value_before = 'http://es:9200'
    edit_value_after = 'http://es2:9200'

# ################################################################################################################################
# Scheduler
# ################################################################################################################################

class TestCRUDScheduler(CRUDTestMixin, unittest.TestCase):
    entity_type = 'scheduler'
    sample_data = {
        'name': 'daily-job',
        'service': 'cleanup.old',
        'job_type': 'interval_based',
        'hours': 24,
    }
    edit_field = 'service'
    edit_value_before = 'cleanup.old'
    edit_value_after = 'cleanup.new'

# ################################################################################################################################

class TestCRUDHolidayCalendar(CRUDTestMixin, unittest.TestCase):
    entity_type = 'holiday_calendar'
    sample_data = {
        'name': 'us-holidays',
        'dates': ['2025-01-01', '2025-07-04'],
        'weekdays': [6, 7],
    }
    edit_field = 'dates'
    edit_value_before = ['2025-01-01', '2025-07-04']
    edit_value_after = ['2025-01-01', '2025-07-04', '2025-12-25']

# ################################################################################################################################
# LDAP
# ################################################################################################################################

class TestCRUDLDAP(CRUDTestMixin, unittest.TestCase):
    entity_type = 'ldap'
    sample_data = {
        'name': 'my-ldap',
        'address': 'ldap://10.0.0.5',
        'port': 389,
        'username': 'cn=admin',
        'password': 'ldap-pass',
    }
    edit_field = 'address'
    edit_value_before = 'ldap://10.0.0.5'
    edit_value_after = 'ldap://10.0.0.6'

# ################################################################################################################################
# PubSub
# ################################################################################################################################

class TestCRUDPubSubTopic(CRUDTestMixin, unittest.TestCase):
    entity_type = 'pubsub_topic'
    sample_data = {
        'name': '/events/order',
        'description': 'Order events',
        'is_active': True,
    }
    edit_field = 'description'
    edit_value_before = 'Order events'
    edit_value_after = 'Updated order events'

# ################################################################################################################################

class _SecurityKeyMixin:
    """Override for entity types keyed by 'security' rather than 'name'."""

    def _name(self):
        return self.sample_data['security']

    def test_create_and_get(self):
        self.cm.set(self.entity_type, self._name(), self.sample_data)
        item = self.cm.get(self.entity_type, self._name())
        self.assertIsNotNone(item)

    def test_edit_field(self):
        self.cm.set(self.entity_type, self._name(), self.sample_data)
        item = self.cm.get(self.entity_type, self._name())
        self.assertEqual(item[self.edit_field], self.edit_value_before)

        updated = dict(self.sample_data)
        updated[self.edit_field] = self.edit_value_after
        self.cm.set(self.entity_type, self._name(), updated)

        item = self.cm.get(self.entity_type, self._name())
        self.assertEqual(item[self.edit_field], self.edit_value_after)

    def test_rename(self):
        self.cm.set(self.entity_type, self._name(), self.sample_data)
        self.cm.delete(self.entity_type, self._name())

        new_name = self._name() + '-renamed'
        renamed_data = dict(self.sample_data)
        self.cm.set(self.entity_type, new_name, renamed_data)

        self.assertIsNone(self.cm.get(self.entity_type, self._name()))
        item = self.cm.get(self.entity_type, new_name)
        self.assertIsNotNone(item)


class TestCRUDPubSubPermission(_SecurityKeyMixin, CRUDTestMixin, unittest.TestCase):
    entity_type = 'pubsub_permission'
    sample_data = {
        'name': 'perm-1',
        'security': 'my-auth',
        'pub': ['/events/order'],
        'sub': ['/events/order'],
    }
    edit_field = 'security'
    edit_value_before = 'my-auth'
    edit_value_after = 'new-auth'

# ################################################################################################################################

class TestCRUDPubSubSubscription(_SecurityKeyMixin, CRUDTestMixin, unittest.TestCase):
    entity_type = 'pubsub_subscription'
    sample_data = {
        'name': 'sub-1',
        'security': 'my-auth',
        'sub_key': 'zpsk.rest.1234',
        'delivery_type': 'pull',
    }
    edit_field = 'delivery_type'
    edit_value_before = 'pull'
    edit_value_after = 'push'

# ################################################################################################################################
# Groups
# ################################################################################################################################

class TestCRUDGroups(CRUDTestMixin, unittest.TestCase):
    entity_type = 'groups'
    sample_data = {
        'name': 'grp-1',
        'members': ['auth-1', 'auth-2'],
    }
    edit_field = 'members'
    edit_value_before = ['auth-1', 'auth-2']
    edit_value_after = ['auth-1', 'auth-2', 'auth-3']

# ################################################################################################################################
# Service
# ################################################################################################################################

class TestCRUDService(CRUDTestMixin, unittest.TestCase):
    entity_type = 'service'
    sample_data = {
        'name': 'my.test.service',
        'impl_name': 'my.test.service.MyTestService',
        'is_active': True,
        'is_internal': False,
        'slow_threshold': 500,
    }
    edit_field = 'slow_threshold'
    edit_value_before = 500
    edit_value_after = 1000

# ################################################################################################################################
# Credential round-trip tests
# ################################################################################################################################

class TestCredentialRoundtrip(unittest.TestCase):

    def setUp(self):
        self.cm = ConfigManager()

    def test_basic_auth_credentials_roundtrip(self):
        self.cm.set('security', 'ba1', {
            'type': 'basic_auth',
            'name': 'ba1',
            'username': 'myuser',
            'password': 'mypass',
            'realm': 'testrealm',
        })
        item = self.cm.get('security', 'ba1')
        self.assertEqual(item['username'], 'myuser')
        self.assertEqual(item['password'], 'mypass')
        self.assertEqual(item['realm'], 'testrealm')

    def test_basic_auth_password_edit_immediate(self):
        self.cm.set('security', 'ba1', {
            'type': 'basic_auth',
            'name': 'ba1',
            'username': 'user1',
            'password': 'old-pass',
        })
        self.assertEqual(self.cm.get('security', 'ba1')['password'], 'old-pass')

        self.cm.set('security', 'ba1', {
            'type': 'basic_auth',
            'name': 'ba1',
            'username': 'user1',
            'password': 'new-pass',
        })
        self.assertEqual(self.cm.get('security', 'ba1')['password'], 'new-pass')

    def test_apikey_credentials_roundtrip(self):
        self.cm.set('security', 'ak1', {
            'type': 'apikey',
            'name': 'ak1',
            'username': 'keyuser',
            'password': 'the-api-key-value',
        })
        item = self.cm.get('security', 'ak1')
        self.assertEqual(item['username'], 'keyuser')
        self.assertEqual(item['password'], 'the-api-key-value')

    def test_credentials_gone_after_delete(self):
        self.cm.set('security', 'ba1', {
            'type': 'basic_auth',
            'name': 'ba1',
            'username': 'user1',
            'password': 'pass1',
        })
        self.cm.delete('security', 'ba1')
        self.assertIsNone(self.cm.get('security', 'ba1'))

    def test_multiple_security_types_coexist(self):
        self.cm.set('security', 'ba1', {
            'type': 'basic_auth', 'name': 'ba1', 'username': 'u1', 'password': 'p1',
        })
        self.cm.set('security', 'ak1', {
            'type': 'apikey', 'name': 'ak1', 'username': 'u2', 'password': 'p2',
        })
        self.cm.set('security', 'nt1', {
            'type': 'ntlm', 'name': 'nt1', 'username': 'u3', 'password': 'p3',
        })
        self.cm.set('security', 'oa1', {
            'type': 'bearer_token', 'name': 'oa1', 'username': 'u4', 'password': 'p4',
        })
        self.cm.set('security', 'bt1', {
            'type': 'bearer_token', 'name': 'bt1', 'username': 'u5', 'password': 'p5',
        })

        items = self.cm.get_list('security')
        self.assertEqual(len(items), 5)

# ################################################################################################################################
# Enmasse round-trip test
# ################################################################################################################################

class TestEnmasseRoundtripBaseline(unittest.TestCase):

    yaml_all_types = '''
security:
  - type: basic_auth
    name: ba-rt
    username: admin
    password: secret
    realm: testrealm
  - type: apikey
    name: ak-rt
    username: keyuser
    password: keyval

groups:
  - name: grp-rt
    members: [ba-rt, ak-rt]

channel_rest:
  - name: /api/rt
    url_path: /api/rt
    service: svc.rt
    method: GET

channel_soap:
  - name: soap-rt
    url_path: /soap/rt
    service: soap.svc
    soap_action: urn:rt

outgoing_rest:
  - name: out-rest-rt
    host: https://api.example.com
    url_path: /v1
    timeout: 30

outgoing_soap:
  - name: out-soap-rt
    host: https://soap.example.com
    url_path: /ws
    soap_action: urn:out
    timeout: 60

scheduler:
  - name: job-rt
    service: job.svc
    job_type: interval_based
    hours: 1

cache:
  - name: cache-rt
    is_default: true
    max_size: 5000

email_smtp:
  - name: smtp-rt
    host: smtp.example.com
    port: 587

email_imap:
  - name: imap-rt
    host: imap.example.com
    port: 993

pubsub_topic:
  - name: /topic/rt
    is_active: true

elastic_search:
  - name: es-rt
    hosts: http://es:9200
    timeout: 15

ldap:
  - name: gen-rt
    address: ldap://10.0.0.5
'''

    def setUp(self):
        self.cm = ConfigManager()
        self.cm.load_yaml_string(self.yaml_all_types)

    def test_all_sections_present_after_load(self):
        exported = self.cm.export_to_dict()
        for section in [
            'security', 'groups', 'channel_rest',
            'outgoing_rest', 'outgoing_soap', 'scheduler', 'cache',
            'email_smtp', 'email_imap', 'pubsub_topic', 'elastic_search',
        ]:
            self.assertIn(section, exported, f'Missing section: {section}')

    def test_security_count(self):
        self.assertEqual(len(self.cm.get_list('security')), 2)

    def test_basic_auth_fields(self):
        item = self.cm.get('security', 'ba-rt')
        self.assertEqual(item['username'], 'admin')
        self.assertEqual(item['password'], 'secret')
        self.assertEqual(item['realm'], 'testrealm')

    def test_apikey_fields(self):
        item = self.cm.get('security', 'ak-rt')
        self.assertEqual(item['username'], 'keyuser')
        self.assertEqual(item['password'], 'keyval')

    def test_channel_rest_fields(self):
        item = self.cm.get('channel_rest', '/api/rt')
        self.assertEqual(item['service'], 'svc.rt')

    def test_outgoing_rest_fields(self):
        item = self.cm.get('outgoing_rest', 'out-rest-rt')
        self.assertEqual(item['host'], 'https://api.example.com')
        self.assertEqual(item['timeout'], 30)

    def test_scheduler_fields(self):
        item = self.cm.get('scheduler', 'job-rt')
        self.assertEqual(item['service'], 'job.svc')
        self.assertEqual(item['hours'], 1)

    def test_idempotent_reload(self):
        self.cm.load_yaml_string(self.yaml_all_types)
        self.assertEqual(len(self.cm.get_list('security')), 2)
        self.assertEqual(len(self.cm.get_list('channel_rest')), 1)

    def test_export_reimport_consistency(self):
        import yaml as _yaml
        exported = self.cm.export_to_dict()

        yaml_str = _yaml.dump(exported, default_flow_style=False)

        cm2 = ConfigManager()
        cm2.load_yaml_string(yaml_str)
        exported2 = cm2.export_to_dict()

        for section in exported:
            self.assertIn(section, exported2, f'{section} missing after reimport')
            self.assertEqual(
                len(exported[section]), len(exported2[section]),
                f'Count mismatch in {section}'
            )

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    unittest.main()
