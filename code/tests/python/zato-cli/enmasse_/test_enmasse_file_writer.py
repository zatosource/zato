# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The file writer and the ordering catalogs it writes from.

# stdlib
import os
from tempfile import gettempdir
from unittest import TestCase, main

# PyYAML
import yaml

# Zato
from zato.cli.enmasse.util import FileWriter, get_object_order, get_top_level_order
from zato.common.crypto.api import CryptoManager

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

    # Add dummy assignments to satisfy type checkers
    any_ = any_
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

# The sections the exporters fill.
_exporter_filled_sections = [
    'mongodb',
    'sftp',
    'smb',
    'channel_amqp',
    'outgoing_amqp',
    'channel_azure_service_bus',
    'outgoing_azure_service_bus',
    'alert_rules',
    'alert_notifications',
    'audit_retention',
    'audit_extraction',
    'rule_engine_api',
]

# ################################################################################################################################
# ################################################################################################################################

class TestTopLevelOrder(TestCase):
    """ The writer's top-level section order.
    """

    def test_every_exporter_filled_section_is_in_the_order(self:'any_') -> 'None':

        top_level = get_top_level_order()

        for name in _exporter_filled_sections:
            self.assertIn(name, top_level)

# ################################################################################################################################

    def test_every_section_in_the_order_has_an_object_order(self:'any_') -> 'None':

        top_level = get_top_level_order()

        for name in top_level:
            fields = get_object_order(name)
            self.assertTrue(fields, f'No object order for `{name}`')

# ################################################################################################################################

    def test_the_documented_fields_are_in_the_object_orders(self:'any_') -> 'None':

        # The fields the reference documents.
        expected = {
            'channel_rest': ['is_audit_log_active', 'method', 'content_type', 'timeout',
                'should_include_in_openapi', 'gateway_service_list:list'],
            'outgoing_rest': ['is_audit_log_active'],
            'channel_soap': ['is_audit_log_active'],
            'outgoing_soap': ['is_audit_log_active', 'use_ws_addressing', 'use_mtom',
                'tls_client_cert', 'tls_client_key', 'body_credentials'],
            'sql': ['extra:list', 'pool_size', 'is_active', 'timeout', 'audit_log'],
            'mcp_gateway': ['invoke_timeout', 'session_ttl'],
        }

        for object_type, field_list in expected.items():
            fields = get_object_order(object_type)
            for name in field_list:
                self.assertIn(name, fields, f'`{name}` not in the `{object_type}` order')

# ################################################################################################################################
# ################################################################################################################################

class TestFileWriter(TestCase):
    """ Writing an enmasse file and reading it back.
    """

    def setUp(self:'any_') -> 'None':
        file_name = 'enmasse.' + CryptoManager.generate_hex_string() + '.yaml'
        self.path = os.path.join(gettempdir(), file_name)

# ################################################################################################################################

    def tearDown(self:'any_') -> 'None':
        os.remove(self.path)

# ################################################################################################################################

    def _write_and_read_back(self:'any_', data:'stranydict') -> 'stranydict':

        # Write the data out ..
        writer = FileWriter(self.path)
        writer.write(data)

        # .. and read it back.
        with open(self.path) as yaml_file:
            out = yaml.safe_load(yaml_file)

        return out

# ################################################################################################################################

    def test_a_mapping_valued_section_is_written_as_flat_scalars(self:'any_') -> 'None':

        # A section whose value is one mapping rather than a list ..
        notifications = {
            'webhook_url': 'https://alerts.example.com/webhooks/operations',
            'email_to': 'ops@example.com',
            'email_from': 'zato@example.com',
            'dashboard_url': 'https://dashboard.example.com',
        }

        # .. round-trips unchanged.
        parsed = self._write_and_read_back({'alert_notifications': notifications})

        self.assertEqual(parsed['alert_notifications'], notifications)

# ################################################################################################################################

    def test_the_sql_extra_list_round_trips(self:'any_') -> 'None':

        # A connection whose extra options are a list ..
        connection = {
            'name': 'enmasse.sql.1',
            'type': 'mysql',
            'host': '127.0.0.1',
            'port': 3306,
            'db_name': 'mydb',
            'username': 'enmasse.1',
            'extra': ['connect_timeout=10', 'charset=utf8mb4'],
        }

        # .. keeps them as a list once read back.
        parsed = self._write_and_read_back({'sql': [connection]})
        written = parsed['sql'][0]

        self.assertEqual(written['extra'], connection['extra'])
        self.assertEqual(written['name'], connection['name'])

# ################################################################################################################################

    def test_a_custom_section_is_written_after_the_static_ones(self:'any_') -> 'None':

        # One static section and one custom one ..
        connection = {
            'name': 'enmasse.sql.1',
            'type': 'mysql',
            'host': '127.0.0.1',
            'port': 3306,
            'db_name': 'mydb',
            'username': 'enmasse.1',
        }

        data = {
            'sql': [connection],
            'custom_crm': [{'name': 'enmasse.custom.crm.1', 'address': 'https://crm.example.com'}],
        }

        # .. and the custom one survives the write.
        parsed = self._write_and_read_back(data)

        custom_crm_list = parsed['custom_crm']
        written = custom_crm_list[0]

        self.assertEqual(written['name'], 'enmasse.custom.crm.1')
        self.assertEqual(written['address'], 'https://crm.example.com')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
