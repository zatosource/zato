# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import tempfile
from unittest import TestCase, main

# PyYAML
import yaml

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.exporter import EnmasseYAMLExporter
from zato.cli.enmasse.exporters.outgoing_soap import OutgoingSOAPExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.outgoing_soap import OutgoingSOAPImporter
from zato.cli.enmasse.util import FileWriter
from zato.common.defaults import default_server_base_dir
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.common.typing_ import any_
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# A connection with every declarative invocation, callback, scheduler and health check field set
_connection_def = {
    'name': 'enmasse.outgoing.soap.declarative',
    'host': 'https://orders.example.com',
    'url_path': '/services/orders',
    'soap_action': 'urn:example:orders:submit',
    'soap_version': '1.1',
    'request_operation': 'SubmitOrder',
    'request_message': [
        {'key': 'order.customer_id', 'value': 'customer-1', 'mode': 'text'},
        {'key': 'order.created_at', 'value': '$now()', 'mode': 'jsonata'},
    ],
    'request_message_map': '$.{ "order": { "id": order_id } }',
    'request_soap_headers': [
        {'key': 'SessionToken', 'value': 'token-value', 'mode': 'text'},
    ],
    'wsa_action': 'urn:example:orders:submit',
    'wsa_to': 'https://orders.example.com/services/orders',
    'wsa_reply_to': 'http://www.w3.org/2005/08/addressing/anonymous',
    'response_map': '//OrderStatus/text()',
    'response_map_mode': 'xpath',
    'callback_type': 'service',
    'callback_name': 'demo.input-logger',
    'scheduler_run_every': 4,
    'scheduler_run_unit': 'hours',
    'scheduler_start_date': '2026-01-01 00:00:00',
    'health_check_run_every': 10,
    'health_check_run_unit': 'minutes',
    'health_check_notify_on': 'all',
    'health_check_callback_type': 'service',
    'health_check_callback_name': 'demo.input-logger',
}

# The names of the row-based fields the connection above carries
_row_field_names = ('request_message', 'request_soap_headers')

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingSOAPDeclarativeExport(TestCase):
    """ Tests that exporting an outgoing SOAP connection carries all its declarative invocation,
    callback, scheduler and health check fields, both in the exported dict and in the written YAML file.
    """

    def setUp(self) -> 'None':
        self.server_path = default_server_base_dir

        # The importer sets up the database state for the export test
        self.importer = EnmasseYAMLImporter()
        self.outgoing_soap_importer = OutgoingSOAPImporter(self.importer)

        # The exporter under test
        self.exporter = EnmasseYAMLExporter()
        self.outgoing_soap_exporter = OutgoingSOAPExporter(self.exporter)

        self.session = cast_('SASession', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
        cleanup_enmasse()

# ################################################################################################################################

    def _import_connection(self) -> 'None':

        self.session = get_session_from_server_dir(self.server_path)
        _ = self.importer.get_cluster(self.session)

        created, updated = self.outgoing_soap_importer.sync_outgoing_soap([dict(_connection_def)], self.session)
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

# ################################################################################################################################

    def _assert_declarative_fields(self, conn:'any_') -> 'None':

        # Scalar fields are exported exactly as they were imported ..
        self.assertEqual(conn['request_operation'], 'SubmitOrder')
        self.assertEqual(conn['request_message_map'], '$.{ "order": { "id": order_id } }')
        self.assertEqual(conn['wsa_action'], 'urn:example:orders:submit')
        self.assertEqual(conn['wsa_to'], 'https://orders.example.com/services/orders')
        self.assertEqual(conn['wsa_reply_to'], 'http://www.w3.org/2005/08/addressing/anonymous')
        self.assertEqual(conn['response_map'], '//OrderStatus/text()')
        self.assertEqual(conn['response_map_mode'], 'xpath')
        self.assertEqual(conn['callback_type'], 'service')
        self.assertEqual(conn['callback_name'], 'demo.input-logger')
        self.assertEqual(conn['scheduler_run_every'], 4)
        self.assertEqual(conn['scheduler_run_unit'], 'hours')
        self.assertEqual(conn['scheduler_start_date'], '2026-01-01 00:00:00')
        self.assertEqual(conn['health_check_run_every'], 10)
        self.assertEqual(conn['health_check_run_unit'], 'minutes')
        self.assertEqual(conn['health_check_notify_on'], 'all')
        self.assertEqual(conn['health_check_callback_type'], 'service')
        self.assertEqual(conn['health_check_callback_name'], 'demo.input-logger')

        # .. row-based fields come out as lists of mappings, not as the JSON strings the database keeps ..
        for field_name in _row_field_names:
            self.assertEqual(conn[field_name], _connection_def[field_name])

        # .. and the environment-local job IDs never travel through enmasse.
        self.assertNotIn('scheduler_job_id', conn)
        self.assertNotIn('health_check_job_id', conn)

# ################################################################################################################################

    def test_outgoing_soap_declarative_export(self) -> 'None':

        self._import_connection()

        # Export the connections and find the one under test
        exported_connections = self.outgoing_soap_exporter.export(self.session, self.importer.cluster_id)

        for conn in exported_connections:
            if conn['name'] == _connection_def['name']:
                break
        else:
            self.fail('Connection `{}` not found in export'.format(_connection_def['name']))

        # The in-memory dict carries every declarative field ..
        self._assert_declarative_fields(conn)

        # .. and so does the YAML file the file writer produces.
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        temp_file.close()

        try:
            writer = FileWriter(temp_file.name)
            writer.write({'outgoing_soap': [conn]})

            with open(temp_file.name) as file_handle:
                written_config = yaml.safe_load(file_handle)

            written_connections = written_config['outgoing_soap']
            self.assertEqual(len(written_connections), 1)

            self._assert_declarative_fields(written_connections[0])
        finally:
            os.unlink(temp_file.name)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
