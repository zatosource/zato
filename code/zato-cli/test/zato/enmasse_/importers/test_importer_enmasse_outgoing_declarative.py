# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import loads
from unittest import TestCase, main

# Zato
from zato.cli.enmasse.client import cleanup_enmasse, get_session_from_server_dir
from zato.cli.enmasse.importer import EnmasseYAMLImporter
from zato.cli.enmasse.importers.outgoing_rest import OutgoingRESTImporter
from zato.cli.enmasse.importers.outgoing_soap import OutgoingSOAPImporter
from zato.common.api import HTTP_SOAP, SchedulerLink
from zato.common.defaults import default_server_base_dir
from zato.common.odb.model import Job
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    SASession = SASession

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_invocation = HTTP_SOAP.Invocation
_health_check = HTTP_SOAP.HealthCheck

# An outgoing REST definition the way a YAML file carries it - row fields as lists of mappings
_rest_def = {
    'name': 'enmasse.outgoing.rest.roundtrip',
    'host': 'https://inventory.example.com',
    'url_path': '/api/items/{item_id}',
    'request_method': 'PUT',
    'request_query_string': [
        {'key': 'status', 'value': 'active', 'mode': 'text'},
    ],
    'request_path_params': [
        {'key': 'item_id', 'value': 'inventory-item-1', 'mode': 'text'},
    ],
    'request_headers': [
        {'key': 'X-Sync-Source', 'value': 'daily-sync', 'mode': 'text'},
    ],
    'callback_type': 'service',
    'callback_name': 'demo.input-logger',
    'scheduler_run_every': 15,
    'scheduler_run_unit': 'minutes',
    'health_check_run_every': 5,
    'health_check_run_unit': 'minutes',
    'health_check_notify_on': 'failures',
    'health_check_callback_type': 'service',
    'health_check_callback_name': 'demo.input-logger',
}

# An outgoing SOAP definition covering the soap. job prefix
_soap_def = {
    'name': 'enmasse.outgoing.soap.roundtrip',
    'host': 'https://orders.example.com',
    'url_path': '/services/orders',
    'soap_action': 'urn:example:orders:submit',
    'soap_version': '1.1',
    'request_operation': 'SubmitOrder',
    'request_message': [
        {'key': 'order.customer_id', 'value': 'customer-1', 'mode': 'text'},
    ],
    'scheduler_run_every': 2,
    'scheduler_run_unit': 'hours',
}

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingDeclarativeImport(TestCase):
    """ Tests that importing outgoing connections with declarative invocation fields re-serializes
    the row fields to JSON strings and recreates the linked scheduler and health check jobs.
    """

    def setUp(self) -> 'None':
        self.server_path = default_server_base_dir

        self.importer = EnmasseYAMLImporter()
        self.outgoing_rest_importer = OutgoingRESTImporter(self.importer)
        self.outgoing_soap_importer = OutgoingSOAPImporter(self.importer)

        self.session = cast_('SASession', None)

# ################################################################################################################################

    def tearDown(self) -> 'None':
        if self.session:
            _ = self.session.close()
        cleanup_enmasse()

# ################################################################################################################################

    def _setup_test_environment(self) -> 'None':
        self.session = get_session_from_server_dir(self.server_path)
        _ = self.importer.get_cluster(self.session)

# ################################################################################################################################

    def _get_job(self, job_name:'str') -> 'Job':
        job = self.session.query(Job).filter_by(name=job_name, cluster_id=self.importer.cluster_id).first()
        self.assertIsNotNone(job, f'Job `{job_name}` was not created')

        return job

# ################################################################################################################################

    def test_rest_import_round_trip(self) -> 'None':

        self._setup_test_environment()

        created, updated = self.outgoing_rest_importer.sync_outgoing_rest([dict(_rest_def)], self.session)
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        conn = created[0]
        opaque = loads(conn.opaque1)

        # Row fields are stored the way the Dashboard stores them - as JSON strings ..
        for field_name in ('request_query_string', 'request_path_params', 'request_headers'):
            stored = opaque[field_name]
            self.assertIsInstance(stored, str, f'Field `{field_name}` should be a JSON string, not `{type(stored)}`')
            self.assertEqual(loads(stored), _rest_def[field_name])

        # .. scalar fields land in the opaque attributes unchanged ..
        self.assertEqual(opaque['request_method'], 'PUT')
        self.assertEqual(opaque['callback_type'], 'service')
        self.assertEqual(opaque['callback_name'], 'demo.input-logger')

        # .. and both linked jobs were created, with their IDs stored back in the opaque attributes.
        scheduler_job = self._get_job('rest.' + _rest_def['name'])
        health_check_job = self._get_job('health.' + _rest_def['name'])

        self.assertEqual(opaque[_invocation.Field_Job_ID], scheduler_job.id)
        self.assertEqual(opaque[_health_check.Field_Job_ID], health_check_job.id)

        # The scheduled-invocation job points back to the connection through the generic link attributes ..
        scheduler_job_opaque = loads(scheduler_job.opaque1)
        self.assertEqual(scheduler_job_opaque[SchedulerLink.Conn_Type], SchedulerLink.ConnType.REST_Outgoing)
        self.assertEqual(scheduler_job_opaque[SchedulerLink.Conn_ID], conn.id)
        self.assertEqual(scheduler_job_opaque[SchedulerLink.Kind], SchedulerLink.KindType.Scheduler)
        self.assertEqual(scheduler_job.service.name, _invocation.Dispatch_Service)

        # .. and so does the health check job.
        health_check_job_opaque = loads(health_check_job.opaque1)
        self.assertEqual(health_check_job_opaque[SchedulerLink.Conn_Type], SchedulerLink.ConnType.REST_Outgoing)
        self.assertEqual(health_check_job_opaque[SchedulerLink.Conn_ID], conn.id)
        self.assertEqual(health_check_job_opaque[SchedulerLink.Kind], SchedulerLink.KindType.HealthCheck)
        self.assertEqual(health_check_job.service.name, _health_check.Dispatch_Service)

        # A second, identical import must be a no-op.
        created, updated = self.outgoing_rest_importer.sync_outgoing_rest([dict(_rest_def)], self.session)
        self.assertEqual(len(created), 0)
        self.assertEqual(len(updated), 0)

# ################################################################################################################################

    def test_soap_import_round_trip(self) -> 'None':

        self._setup_test_environment()

        created, updated = self.outgoing_soap_importer.sync_outgoing_soap([dict(_soap_def)], self.session)
        self.assertEqual(len(created), 1)
        self.assertEqual(len(updated), 0)

        conn = created[0]
        opaque = loads(conn.opaque1)

        # Message rows are stored as a JSON string ..
        stored = opaque['request_message']
        self.assertIsInstance(stored, str)
        self.assertEqual(loads(stored), _soap_def['request_message'])

        # .. and the linked job carries the soap. prefix and the generic link attributes.
        scheduler_job = self._get_job('soap.' + _soap_def['name'])
        self.assertEqual(opaque[_invocation.Field_Job_ID], scheduler_job.id)

        scheduler_job_opaque = loads(scheduler_job.opaque1)
        self.assertEqual(scheduler_job_opaque[SchedulerLink.Conn_Type], SchedulerLink.ConnType.SOAP_Outgoing)
        self.assertEqual(scheduler_job_opaque[SchedulerLink.Conn_ID], conn.id)
        self.assertEqual(scheduler_job_opaque[SchedulerLink.Kind], SchedulerLink.KindType.Scheduler)
        self.assertEqual(scheduler_job.service.name, _invocation.Dispatch_Service)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
