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
from zato.cli.enmasse.exporters.outgoing_rest import OutgoingRESTExporter
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.outgoing_rest import OutgoingRESTImporter
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
    'name': 'enmasse.outgoing.rest.declarative',
    'host': 'https://inventory.example.com',
    'url_path': '/api/items/{item_id}',
    'request_method': 'PUT',
    'request_query_string': [
        {'key': 'status', 'value': 'active', 'mode': 'text'},
        {'key': 'since', 'value': '$fromMillis($toMillis($now()) - 86400000, \'[Y0001]-[M01]-[D01]\')', 'mode': 'jsonata'},
    ],
    'request_path_params': [
        {'key': 'item_id', 'value': '123', 'mode': 'text'},
    ],
    'request_headers': [
        {'key': 'X-Sync-Source', 'value': 'daily-sync', 'mode': 'text'},
    ],
    'request_data': '{"is_full_sync": true}',
    'request_data_mode': 'text',
    'response_map': '$.{ "id": item_id, "is_available": stock_count > reserved_count }',
    'response_map_mode': 'jsonata',
    'callback_type': 'service',
    'callback_name': 'demo.input-logger',
    'scheduler_run_every': 30,
    'scheduler_run_unit': 'minutes',
    'scheduler_start_date': '2026-01-01 00:00:00',
    'health_check_run_every': 5,
    'health_check_run_unit': 'minutes',
    'health_check_notify_on': 'failures',
    'health_check_callback_type': 'topic',
    'health_check_callback_name': 'inventory.health-checks',
}

# The names of the row-based fields the connection above carries
_row_field_names = ('request_query_string', 'request_path_params', 'request_headers')

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingRESTDeclarativeExport(TestCase):
    """ Tests that exporting an outgoing REST connection carries all its declarative invocation,
    callback, scheduler and health check fields, both in the exported dict and in the written YAML file.
    """

    def setUp(self) -> 'None':
        self.server_path = default_server_base_dir

        # The importer sets up the database state for the export test
        self.importer = EnmasseYAMLImporter()
        self.outgoing_rest_importer = OutgoingRESTImporter(self.importer)

        # The exporter under test
        self.exporter = EnmasseYAMLExporter()
        self.outgoing_rest_exporter = OutgoingRESTExporter(self.exporter)

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

        created, updated = self.outgoing_rest_importer.sync_outgoing_rest([dict(_connection_def)], self.session)
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

# ################################################################################################################################

    def _assert_declarative_fields(self, conn:'any_') -> 'None':

        # Scalar fields are exported exactly as they were imported ..
        self.assertEqual(conn['request_method'], 'PUT')
        self.assertEqual(conn['request_data'], '{"is_full_sync": true}')
        self.assertEqual(conn['request_data_mode'], 'text')
        self.assertEqual(conn['response_map'], '$.{ "id": item_id, "is_available": stock_count > reserved_count }')
        self.assertEqual(conn['response_map_mode'], 'jsonata')
        self.assertEqual(conn['callback_type'], 'service')
        self.assertEqual(conn['callback_name'], 'demo.input-logger')
        self.assertEqual(conn['scheduler_run_every'], 30)
        self.assertEqual(conn['scheduler_run_unit'], 'minutes')
        self.assertEqual(conn['scheduler_start_date'], '2026-01-01 00:00:00')
        self.assertEqual(conn['health_check_run_every'], 5)
        self.assertEqual(conn['health_check_run_unit'], 'minutes')
        self.assertEqual(conn['health_check_notify_on'], 'failures')
        self.assertEqual(conn['health_check_callback_type'], 'topic')
        self.assertEqual(conn['health_check_callback_name'], 'inventory.health-checks')

        # .. row-based fields come out as lists of mappings, not as the JSON strings the database keeps ..
        for field_name in _row_field_names:
            self.assertEqual(conn[field_name], _connection_def[field_name])

        # .. and the environment-local job IDs never travel through enmasse.
        self.assertNotIn('scheduler_job_id', conn)
        self.assertNotIn('health_check_job_id', conn)

# ################################################################################################################################

    def test_outgoing_rest_declarative_export(self) -> 'None':

        self._import_connection()

        # Export the connections and find the one under test
        exported_connections = self.outgoing_rest_exporter.export(self.session, self.importer.cluster_id)

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
            writer.write({'outgoing_rest': [conn]})

            with open(temp_file.name) as file_handle:
                written_config = yaml.safe_load(file_handle)

            written_connections = written_config['outgoing_rest']
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
