# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timezone
from json import dumps
from unittest import TestCase

# OpenTelemetry
from opentelemetry.proto.logs.v1.logs_pb2 import SEVERITY_NUMBER_ERROR, SEVERITY_NUMBER_INFO, SEVERITY_NUMBER_WARN

# Zato
from support import attributes_of, build_queued, to_queued, CapturingAuditLog, Server_Name
from zato.common.api import SCHEDULER
from zato.common.audit_log.calls import record_remote_call
from zato.common.audit_log.common import AuditBody, AuditEvent, AuditOutcome, AuditSource, LLMAttr, MCPAttr
from zato.common.audit_log.config_audit import record_config_change, ConfigScope
from zato.common.audit_log.export.data import ModuleCtx as DataCtx
from zato.common.audit_log.export.mapping import build_log_record, severity_by_outcome, ModuleCtx
from zato.common.audit_log.file_transfer import record_file_transfer
from zato.common.audit_log.scheduler import record_job_start
from zato.common.audit_log.sql import record_sql_execution, Level_Full
from zato.common.alerting.engine import record_alert_event
from zato.common.alerting.model import AlertRule, Finding
from zato.common.bearer_token_identity import build_auth_block, Auth_Type_Bearer_JWT
from zato.common.hl7.audit import audit_message_received
from zato.common.model.security import BearerAuthInfo, BearerRefusalReason
from zato.server.connection.mcp.audit import build_audit_event, build_rate_limit_audit_event

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.buffer import PendingEvent
    from zato.common.typing_ import any_, anytuple, stranydict

# ################################################################################################################################
# ################################################################################################################################

# What every MCP event uses unless a test overrides it
_gateway_name = 'billing'
_sec_def_name = 'mcp.billing.agents'
_cid = 'cid-mcp-1'
_session_id = 'mcp0123456789'
_remote_address = '10.20.30.40'
_identity = 'maria.johnson@example.com'

# The default payload cap the tests build records with
_max_payload_size = 65536

# ################################################################################################################################
# ################################################################################################################################

def _column(name:'str') -> 'str':
    out = f'{ModuleCtx.Prefix}.{name}'
    return out

def _attr(name:'str') -> 'str':
    out = f'{ModuleCtx.Attr_Prefix}.{name}'
    return out

def _data(name:'str') -> 'str':
    out = f'{DataCtx.Data_Prefix}.{name}'
    return out

def _payload(name:'str') -> 'str':
    out = f'{DataCtx.Payload_Prefix}.{name}'
    return out

# ################################################################################################################################

def _build_record(pending:'PendingEvent', *, is_payload_active:'bool'=False, max_payload_size:'int'=_max_payload_size) -> 'anytuple':
    """ Builds the record of one written event and returns it with its attributes as a dict.
    """
    event = to_queued(pending, is_payload_active=is_payload_active)
    record = build_log_record(event, max_payload_size)
    attributes = attributes_of(record)

    out = record, attributes
    return out

# ################################################################################################################################

def _build_auth_info(**overrides:'any_') -> 'BearerAuthInfo':
    """ An accepted JWT caller unless a test overrides it.
    """
    out = BearerAuthInfo()
    out.is_ok = True
    out.security_id = 1
    out.sec_def_name = _sec_def_name
    out.identity_claim = 'email'
    out.identity = _identity
    out.is_jwt = True
    out.claims = {
        'iss': 'https://login.example.com/tenant',
        'aud': 'api://zato-mcp',
        'azp': 'agent-client-id',
        'scp': 'api://zato-mcp/tools.access api://zato-mcp/tools.read',
        'jti': 'token-id-1',
        'exp': 1900000000,
        'email': _identity,
    }
    out.claims_matched = ['groups']

    for name, value in overrides.items():
        setattr(out, name, value)

    return out

# ################################################################################################################################

def _build_mcp_event(**overrides:'any_') -> 'stranydict':
    """ Calls build_audit_event with the defaults of one accepted tools/call.
    """
    kwargs:'stranydict' = {
        'gateway_name': _gateway_name,
        'sec_def_name': f'{_sec_def_name}/{_identity}',
        'cid': _cid,
        'method': 'tools/call',
        'tool_name': 'billing.invoice.get',
        'session_id': _session_id,
        'remote_address': _remote_address,
        'response_body': {'jsonrpc': '2.0', 'id': 1, 'result': {'content': []}},
        'response_size': 512,
        'status_code': 200,
        'duration_ms': 12.345,
        'request_size': 256,
        'trace': {'pii_removed': {'email': 2}},
        'auth': build_auth_block(_build_auth_info()),
    }
    kwargs.update(overrides)

    out = build_audit_event(**kwargs)
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRecordShape(TestCase):

    def setUp(self) -> 'None':
        self.audit_log = CapturingAuditLog()

# ################################################################################################################################

    def test_timestamp_event_name_body_and_columns(self) -> 'None':

        event = build_queued(
            event_id=77,
            cid='cid-1',
            cid_sequence=3,
            source=AuditSource.REST_Channel,
            event_type=AuditEvent.Request_Received,
            object_name='billing.invoices',
            event_time_iso='2026-03-01T10:20:30.123456+00:00',
            endpoint='/billing/invoices',
            size=120,
            outcome=AuditOutcome.OK,
            duration_ms=0,
            data='{"invoice_id": "INV-1"}',
        )

        record = build_log_record(event, _max_payload_size)
        attributes = attributes_of(record)

        # The event time is the record's time and the hand-off time is when it was observed ..
        expected_time = datetime(2026, 3, 1, 10, 20, 30, 123456, tzinfo=timezone.utc)
        expected_ns = int(expected_time.timestamp()) * 1_000_000_000 + 123456 * 1000

        self.assertEqual(record.time_unix_nano, expected_ns)
        self.assertEqual(record.observed_time_unix_nano, event.observed_ns)

        # .. the event name and the body are what a log viewer shows ..
        self.assertEqual(record.event_name, 'zato.audit.request-received')
        self.assertEqual(record.body.string_value, 'rest-channel request-received billing.invoices ok')

        # .. every column that is set is an attribute, numbers always ..
        self.assertEqual(attributes[ModuleCtx.Event_ID], 77)
        self.assertEqual(attributes[_column('source')], AuditSource.REST_Channel)
        self.assertEqual(attributes[_column('event_type')], AuditEvent.Request_Received)
        self.assertEqual(attributes[_column('object_name')], 'billing.invoices')
        self.assertEqual(attributes[_column('cid')], 'cid-1')
        self.assertEqual(attributes[_column('cid_sequence')], 3)
        self.assertEqual(attributes[_column('endpoint')], '/billing/invoices')
        self.assertEqual(attributes[_column('size')], 120)
        self.assertEqual(attributes[_column('priority')], 0)
        self.assertEqual(attributes[_column('duration_ms')], 0)
        self.assertEqual(attributes[_column('outcome')], AuditOutcome.OK)

        # .. empty strings are left out ..
        self.assertNotIn(_column('msg_id'), attributes)
        self.assertNotIn(_column('correl_id'), attributes)
        self.assertNotIn(_column('ext_client_id'), attributes)
        self.assertNotIn(_column('sub_key'), attributes)
        self.assertNotIn(_column('status'), attributes)
        self.assertNotIn(_column('application_outcome'), attributes)
        self.assertNotIn(_column('classification'), attributes)
        self.assertNotIn(_column('pub_time_iso'), attributes)

        # .. server_name is a resource attribute and data of a REST channel never leaves without the payload flag.
        self.assertNotIn(_column('server_name'), attributes)
        self.assertNotIn(_column('data'), attributes)

        for name in attributes:
            self.assertFalse(name.startswith(DataCtx.Data_Prefix), name)
            self.assertFalse(name.startswith(DataCtx.Payload_Prefix), name)

# ################################################################################################################################

    def test_severity_of_every_outcome_a_writer_uses(self) -> 'None':

        expected = {
            '':                                          (SEVERITY_NUMBER_INFO,  'INFO'),
            AuditOutcome.OK:                             (SEVERITY_NUMBER_INFO,  'INFO'),
            AuditOutcome.Running:                        (SEVERITY_NUMBER_INFO,  'INFO'),
            AuditOutcome.Expired:                        (SEVERITY_NUMBER_WARN,  'WARN'),
            AuditOutcome.Error:                          (SEVERITY_NUMBER_ERROR, 'ERROR'),
            SCHEDULER.OUTCOME.OK:                        (SEVERITY_NUMBER_INFO,  'INFO'),
            SCHEDULER.OUTCOME.ERROR:                     (SEVERITY_NUMBER_ERROR, 'ERROR'),
            SCHEDULER.OUTCOME.RUNNING:                   (SEVERITY_NUMBER_INFO,  'INFO'),
            SCHEDULER.OUTCOME.TIMEOUT:                   (SEVERITY_NUMBER_ERROR, 'ERROR'),
            SCHEDULER.OUTCOME.SKIPPED_ALREADY_IN_FLIGHT: (SEVERITY_NUMBER_WARN,  'WARN'),
        }

        for outcome, severity in expected.items():
            self.assertIn(outcome, severity_by_outcome, outcome)
            self.assertEqual(severity_by_outcome[outcome], severity, outcome)

            event = build_queued(outcome=outcome)
            record = build_log_record(event, _max_payload_size)

            self.assertEqual(record.severity_number, severity[0], outcome)
            self.assertEqual(record.severity_text, severity[1], outcome)

# ################################################################################################################################

    def test_attrs_keep_their_types(self) -> 'None':

        attrs = {
            'level': 'full',
            'duration_ms': 12,
            'ratio': 0.5,
            'is_ok': True,
            'missing': None,
        }

        event = build_queued(attrs=attrs)
        record = build_log_record(event, _max_payload_size)

        for key_value in record.attributes:
            if key_value.key == _attr('level'):
                self.assertEqual(key_value.value.WhichOneof('value'), 'string_value')
            elif key_value.key == _attr('duration_ms'):
                self.assertEqual(key_value.value.WhichOneof('value'), 'int_value')
            elif key_value.key == _attr('ratio'):
                self.assertEqual(key_value.value.WhichOneof('value'), 'double_value')
            elif key_value.key == _attr('is_ok'):
                self.assertEqual(key_value.value.WhichOneof('value'), 'bool_value')

        attributes = attributes_of(record)

        self.assertEqual(attributes[_attr('level')], 'full')
        self.assertEqual(attributes[_attr('duration_ms')], 12)
        self.assertEqual(attributes[_attr('ratio')], 0.5)
        self.assertIs(attributes[_attr('is_ok')], True)
        self.assertNotIn(_attr('missing'), attributes)

# ################################################################################################################################
# ################################################################################################################################

class TestMCP(TestCase):

    def setUp(self) -> 'None':
        self.audit_log = CapturingAuditLog()

# ################################################################################################################################

    def test_tools_call(self) -> 'None':

        event = _build_mcp_event()
        _ = self.audit_log.insert(**event)

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.mcp-tools-call')
        self.assertEqual(record.severity_text, 'INFO')
        self.assertEqual(record.body.string_value, 'mcp mcp-tools-call billing ok')

        # Columns ..
        self.assertEqual(attributes[_column('source')], AuditSource.MCP)
        self.assertEqual(attributes[_column('object_name')], _gateway_name)
        self.assertEqual(attributes[_column('endpoint')], 'billing.invoice.get')
        self.assertEqual(attributes[_column('ext_client_id')], f'{_sec_def_name}/{_identity}')
        self.assertEqual(attributes[_column('sub_key')], _session_id)
        self.assertEqual(attributes[_column('size')], 512)
        self.assertEqual(attributes[_column('duration_ms')], 13)
        self.assertEqual(attributes[_column('cid')], _cid)

        # .. attrs with their types ..
        self.assertEqual(attributes[_attr(MCPAttr.Method)], 'tools/call')
        self.assertEqual(attributes[_attr(MCPAttr.Request_Size)], 256)
        self.assertEqual(attributes[_attr(MCPAttr.Identity)], _identity)
        self.assertEqual(attributes[_attr(MCPAttr.Client)], 'agent-client-id')
        self.assertNotIn(_attr(MCPAttr.Reason), attributes)
        self.assertNotIn(_attr(MCPAttr.Error_Code), attributes)

        # .. the whole data document, flattened ..
        self.assertEqual(attributes[_data('remote_address')], _remote_address)
        self.assertEqual(attributes[_data('method')], 'tools/call')
        self.assertEqual(attributes[_data('duration_ms')], 12.35)
        self.assertEqual(attributes[_data('request_size')], 256)
        self.assertEqual(attributes[_data('pii_removed.email')], 2)

        # .. and the auth block as it is.
        self.assertEqual(attributes[_data('auth.type')], Auth_Type_Bearer_JWT)
        self.assertEqual(attributes[_data('auth.definition')], _sec_def_name)
        self.assertEqual(attributes[_data('auth.identity')], _identity)
        self.assertEqual(attributes[_data('auth.issuer')], 'https://login.example.com/tenant')
        self.assertEqual(attributes[_data('auth.audience')], 'api://zato-mcp')
        self.assertEqual(attributes[_data('auth.client')], 'agent-client-id')
        self.assertEqual(attributes[_data('auth.scopes')], ['api://zato-mcp/tools.access', 'api://zato-mcp/tools.read'])
        self.assertEqual(attributes[_data('auth.token_id')], 'token-id-1')
        self.assertEqual(attributes[_data('auth.expires_at')], 1900000000)
        self.assertEqual(attributes[_data('auth.claims_matched')], ['groups'])
        self.assertNotIn(_data('auth.reason'), attributes)
        self.assertNotIn(_data('auth.claim'), attributes)

        # No payload ever leaves an MCP record
        for name in attributes:
            self.assertFalse(name.startswith(DataCtx.Payload_Prefix), name)

# ################################################################################################################################

    def test_audience_list_stays_an_array(self) -> 'None':

        info = _build_auth_info()
        info.claims['aud'] = ['api://zato-mcp', 'api://zato-other']

        event = _build_mcp_event(auth=build_auth_block(info))
        _ = self.audit_log.insert(**event)

        _, attributes = _build_record(self.audit_log.last())

        self.assertEqual(attributes[_data('auth.audience')], ['api://zato-mcp', 'api://zato-other'])

# ################################################################################################################################

    def test_each_refusal_reason(self) -> 'None':

        reasons = []
        for name, value in vars(BearerRefusalReason).items():
            if name.startswith('_'):
                continue
            if isinstance(value, str):
                reasons.append(value)

        self.assertGreater(len(reasons), 5)

        for reason in reasons:

            info = _build_auth_info(is_ok=False, reason=reason, claim='groups', identity='', claims_matched=[])
            auth = build_auth_block(info)

            event = _build_mcp_event(
                method='tools/call',
                response_body={'jsonrpc': '2.0', 'id': 1, 'error': {'code': -32001, 'message': 'Unauthorized'}},
                status_code=401,
                auth=auth,
            )
            _ = self.audit_log.insert(**event)

            record, attributes = _build_record(self.audit_log.last())

            self.assertEqual(record.severity_text, 'ERROR', reason)
            self.assertEqual(attributes[_column('outcome')], AuditOutcome.Error, reason)
            self.assertEqual(attributes[_data('auth.reason')], reason, reason)
            self.assertEqual(attributes[_data('auth.claim')], 'groups', reason)
            self.assertEqual(attributes[_attr(MCPAttr.Reason)], reason, reason)
            self.assertEqual(attributes[_attr(MCPAttr.Error_Code)], -32001, reason)
            self.assertEqual(attributes[_data('error_code')], -32001, reason)
            self.assertEqual(attributes[_data('error_message')], 'Unauthorized', reason)

            # A refused caller with no identity has no identity attribute
            self.assertNotIn(_attr(MCPAttr.Identity), attributes, reason)
            self.assertNotIn(_data('auth.identity'), attributes, reason)

# ################################################################################################################################

    def test_rate_limited(self) -> 'None':

        event = build_rate_limit_audit_event(_gateway_name, _sec_def_name, _cid, _session_id, _remote_address, 3600, 256)
        _ = self.audit_log.insert(**event)

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.rate-limited')
        self.assertEqual(record.severity_text, 'ERROR')

        self.assertEqual(attributes[_column('ext_client_id')], _sec_def_name)
        self.assertEqual(attributes[_column('sub_key')], _session_id)
        self.assertNotIn(_column('endpoint'), attributes)

        self.assertEqual(attributes[_data('retry_after_seconds')], 3600)
        self.assertEqual(attributes[_data('remote_address')], _remote_address)
        self.assertEqual(attributes[_data('request_size')], 256)

        # A rate-limited event has no auth block
        for name in attributes:
            self.assertFalse(name.startswith(_data('auth')), name)

# ################################################################################################################################
# ################################################################################################################################

class TestSources(TestCase):

    def setUp(self) -> 'None':
        self.audit_log = CapturingAuditLog()

# ################################################################################################################################

    def _assert_no_data_or_payload(self, attributes:'stranydict') -> 'None':
        for name in attributes:
            self.assertFalse(name.startswith(DataCtx.Data_Prefix), name)
            self.assertFalse(name.startswith(DataCtx.Payload_Prefix), name)

# ################################################################################################################################

    def test_rest_channel(self) -> 'None':

        _ = self.audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, 'billing.invoices',
            cid='cid-rest-1', endpoint='/billing/invoices', size=64, outcome=AuditOutcome.OK, status='200',
            duration_ms=7, data='{"status": "accepted"}')

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.response-sent')
        self.assertEqual(record.severity_text, 'INFO')
        self.assertEqual(attributes[_column('source')], AuditSource.REST_Channel)
        self.assertEqual(attributes[_column('status')], '200')
        self.assertEqual(attributes[_column('duration_ms')], 7)
        self.assertEqual(attributes[_column('size')], 64)

        self._assert_no_data_or_payload(attributes)

# ################################################################################################################################

    def test_soap_channel(self) -> 'None':

        _ = self.audit_log.insert(AuditSource.SOAP_Channel, AuditEvent.Request_Received, 'crm.soap',
            cid='cid-soap-1', endpoint='/soap/crm', size=800, outcome=AuditOutcome.Error, status='500',
            application_outcome='soap:Server', data='<soap:Envelope/>', bodies={AuditBody.Request: '<soap:Envelope/>'})

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.severity_text, 'ERROR')
        self.assertEqual(attributes[_column('source')], AuditSource.SOAP_Channel)
        self.assertEqual(attributes[_column('application_outcome')], 'soap:Server')
        self.assertEqual(attributes[_column('classification')], self.audit_log.last().values['classification'])

        self._assert_no_data_or_payload(attributes)

# ################################################################################################################################

    def test_rest_outgoing(self) -> 'None':

        _ = self.audit_log.insert(AuditSource.REST_Outgoing, AuditEvent.Response_Received, 'crm.api',
            cid='cid-out-1', endpoint='https://crm.example.com/customers/1', size=300, outcome=AuditOutcome.OK,
            status='200', duration_ms=42, data='{"customer_id": 1}', bodies={AuditBody.Response: '{"customer_id": 1}'})

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.body.string_value, 'rest-outgoing response-received crm.api ok')
        self.assertEqual(attributes[_column('endpoint')], 'https://crm.example.com/customers/1')
        self.assertEqual(attributes[_column('duration_ms')], 42)

        self._assert_no_data_or_payload(attributes)

# ################################################################################################################################

    def test_sql_outgoing(self) -> 'None':

        rows = [{'id': 1, 'name': 'a'}, {'id': 2, 'name': 'b'}]

        _ = record_sql_execution(self.audit_log, 'crm.db', Level_Full, 'select id, name from customers where id > :id',
            cid='cid-sql-1', endpoint='crm.lookup', outcome=AuditOutcome.OK, params={'id': 0}, rows=rows, duration_ms=5)

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.request-sent')
        self.assertEqual(attributes[_column('source')], AuditSource.SQL_Outgoing)
        self.assertEqual(attributes[_attr('level')], Level_Full)
        self.assertEqual(attributes[_attr('duration_ms')], 5)

        # Only the statement, the row count and the error leave
        self.assertEqual(attributes[_data('statement')], 'select id, name from customers where id > :id')
        self.assertEqual(attributes[_data('row_count')], 2)
        self.assertNotIn(_data('error'), attributes)
        self.assertNotIn(_data('params.id'), attributes)
        self.assertNotIn(_data('rows'), attributes)

        # A failed statement names its error
        _ = record_sql_execution(self.audit_log, 'crm.db', Level_Full, 'select 1',
            cid='cid-sql-2', endpoint='crm.lookup', outcome=AuditOutcome.Error, error='no such table')

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.severity_text, 'ERROR')
        self.assertEqual(attributes[_data('error')], 'no such table')

# ################################################################################################################################

    def test_fhir(self) -> 'None':

        stored = dumps({
            'payload': '{"resourceType": "Patient"}',
            'method': 'post',
            'path': '/Patient',
            'params': {'_format': 'json'},
        })

        _ = self.audit_log.insert(AuditSource.FHIR, AuditEvent.Request_Sent, 'ehr.fhir',
            cid='cid-fhir-1', endpoint='POST /Patient', size=30, outcome=AuditOutcome.OK, data=stored,
            attrs={'resource_type': 'Patient', 'method': 'POST'})

        _, attributes = _build_record(self.audit_log.last())

        self.assertEqual(attributes[_attr('resource_type')], 'Patient')
        self.assertEqual(attributes[_attr('method')], 'POST')
        self.assertEqual(attributes[_data('method')], 'post')
        self.assertEqual(attributes[_data('path')], '/Patient')
        self.assertNotIn(_data('payload'), attributes)
        self.assertNotIn(_data('params._format'), attributes)

# ################################################################################################################################

    def test_email_imap(self) -> 'None':

        summary = dumps({
            'subject': 'Monthly report',
            'sent_from': 'reports@example.com',
            'sent_to': 'finance@example.com',
            'body': 'Please find the report attached',
        })

        _ = self.audit_log.insert(AuditSource.Email_IMAP, AuditEvent.Message_Received, 'reports.imap',
            cid='cid-imap-1', endpoint='INBOX', msg_id='<message-id-1@example.com>', size=2048, outcome=AuditOutcome.OK,
            data=summary)

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.message-received')
        self.assertEqual(attributes[_column('msg_id')], '<message-id-1@example.com>')
        self.assertEqual(attributes[_data('sent_from')], 'reports@example.com')
        self.assertEqual(attributes[_data('sent_to')], 'finance@example.com')
        self.assertNotIn(_data('subject'), attributes)
        self.assertNotIn(_data('body'), attributes)

# ################################################################################################################################

    def test_email_smtp(self) -> 'None':

        _ = self.audit_log.insert(AuditSource.Email_SMTP, AuditEvent.Request_Sent, 'alerts.smtp',
            cid='cid-smtp-1', endpoint='ops@example.com', size=512, outcome=AuditOutcome.OK, duration_ms=120,
            data='{"subject": "Alert", "to": ["ops@example.com"]}')

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.body.string_value, 'email-smtp request-sent alerts.smtp ok')
        self.assertEqual(attributes[_column('endpoint')], 'ops@example.com')

        self._assert_no_data_or_payload(attributes)

# ################################################################################################################################

    def test_file_outgoing(self) -> 'None':

        _ = record_file_transfer(self.audit_log, 'reports.sftp', 'upload', '/outgoing/report.csv',
            cid='cid-file-1', outcome=AuditOutcome.OK, size=4096, duration_ms=250, checksum='abc123',
            content=b'a,b,c', extra={'verified': True})

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.request-sent')
        self.assertEqual(attributes[_column('source')], AuditSource.File_Outgoing)
        self.assertEqual(attributes[_column('endpoint')], '/outgoing/report.csv')
        self.assertEqual(attributes[_column('size')], 4096)

        self.assertEqual(attributes[_attr('operation')], 'upload')
        self.assertEqual(attributes[_attr('duration_ms')], 250)
        self.assertEqual(attributes[_attr('checksum')], 'abc123')

        # The whole run summary leaves, the attachment never does
        self.assertEqual(attributes[_data('operation')], 'upload')
        self.assertEqual(attributes[_data('remote_path')], '/outgoing/report.csv')
        self.assertEqual(attributes[_data('size')], 4096)
        self.assertIs(attributes[_data('verified')], True)

        for name in attributes:
            self.assertFalse(name.startswith(DataCtx.Payload_Prefix), name)

        self.assertNotIn('a,b,c', str(attributes))

# ################################################################################################################################

    def test_scheduler(self) -> 'None':

        _ = record_job_start(self.audit_log, 'nightly.cleanup',
            cid='cid-job-1', job_id=12, current_run=3, planned_fire_time_iso='2026-03-01T02:00:00+00:00',
            delay_ms=15, service='demo.cleanup')

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.job-executed')
        self.assertEqual(record.severity_text, 'INFO')
        self.assertEqual(attributes[_column('outcome')], SCHEDULER.OUTCOME.RUNNING)
        self.assertEqual(attributes[_column('endpoint')], 'demo.cleanup')
        self.assertEqual(attributes[_column('pub_time_iso')], '2026-03-01T02:00:00+00:00')

        self.assertEqual(attributes[_attr('job_id')], 12)
        self.assertEqual(attributes[_attr('current_run')], 3)
        self.assertEqual(attributes[_attr('delay_ms')], 15)

        self._assert_no_data_or_payload(attributes)

# ################################################################################################################################

    def test_config(self) -> 'None':

        _ = record_config_change(self.audit_log,
            action=AuditEvent.Config_Edited, object_type='channel_rest', object_name='billing.invoices',
            actor='admin', cid='cid-config-1', effective_actor='root', scope=ConfigScope.Persistent,
            before={'url_path': '/old', 'password': 'secret-1'}, after={'url_path': '/new', 'password': 'secret-2'})

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.config-edited')
        self.assertEqual(attributes[_column('source')], AuditSource.Config)

        self.assertEqual(attributes[_attr('actor')], 'admin')
        self.assertEqual(attributes[_attr('effective_actor')], 'root')
        self.assertEqual(attributes[_attr('scope')], ConfigScope.Persistent)
        self.assertEqual(attributes[_attr('object_type')], 'channel_rest')

        # The before and after summary leaves in full, with the secret masked by the writer
        self.assertEqual(attributes[_data('object_type')], 'channel_rest')
        self.assertEqual(attributes[_data('before.url_path')], '/old')
        self.assertEqual(attributes[_data('after.url_path')], '/new')
        self.assertIn(_data('before.password'), attributes)
        self.assertNotIn('secret-1', str(attributes))
        self.assertNotIn('secret-2', str(attributes))

# ################################################################################################################################

    def test_llm(self) -> 'None':

        attrs = {
            LLMAttr.Model: 'gpt-4.1',
            LLMAttr.Finish_Reason: 'stop',
            LLMAttr.Input_Tokens: 120,
            LLMAttr.Output_Tokens: 48,
        }

        record_remote_call(self.audit_log, AuditSource.LLM, 'openai.main',
            cid='cid-llm-1', is_ok=True, duration_ms=900, status='200', endpoint='https://api.openai.com/v1', attrs=attrs)

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.response-received')
        self.assertEqual(record.severity_text, 'INFO')
        self.assertEqual(attributes[_column('source')], AuditSource.LLM)

        self.assertEqual(attributes[_attr(LLMAttr.Model)], 'gpt-4.1')
        self.assertEqual(attributes[_attr(LLMAttr.Finish_Reason)], 'stop')
        self.assertEqual(attributes[_attr(LLMAttr.Input_Tokens)], 120)
        self.assertEqual(attributes[_attr(LLMAttr.Output_Tokens)], 48)

        self._assert_no_data_or_payload(attributes)

        # A credentials failure is its own event type
        record_remote_call(self.audit_log, AuditSource.LLM, 'openai.main',
            cid='cid-llm-2', is_ok=False, is_auth_error=True, status='401', endpoint='https://api.openai.com/v1', attrs={})

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.auth-failed')
        self.assertEqual(record.severity_text, 'ERROR')

# ################################################################################################################################

    def test_pubsub(self) -> 'None':

        _ = self.audit_log.insert(AuditSource.PubSub, AuditEvent.Published, 'orders.created',
            cid='cid-pub-1', msg_id='zpsm-1', correl_id='order-1', ext_client_id='orders.publisher',
            pub_time_iso='2026-03-01T10:00:00+00:00', sub_key='zpsk-1', size=256, priority=5, outcome=AuditOutcome.OK,
            data='{"order_id": 1}', bodies={AuditBody.Request: '{"order_id": 1}'})

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.published')
        self.assertEqual(attributes[_column('msg_id')], 'zpsm-1')
        self.assertEqual(attributes[_column('correl_id')], 'order-1')
        self.assertEqual(attributes[_column('ext_client_id')], 'orders.publisher')
        self.assertEqual(attributes[_column('pub_time_iso')], '2026-03-01T10:00:00+00:00')
        self.assertEqual(attributes[_column('sub_key')], 'zpsk-1')
        self.assertEqual(attributes[_column('priority')], 5)

        self._assert_no_data_or_payload(attributes)

        # An expired message is a warning
        _ = self.audit_log.insert(AuditSource.PubSub, AuditEvent.Expired, 'orders.created',
            cid='cid-pub-2', msg_id='zpsm-2', outcome=AuditOutcome.Expired)

        record, _ = _build_record(self.audit_log.last())

        self.assertEqual(record.severity_text, 'WARN')
        self.assertEqual(record.severity_number, SEVERITY_NUMBER_WARN)

# ################################################################################################################################

    def test_kafka(self) -> 'None':

        _ = self.audit_log.insert(AuditSource.Kafka_Outgoing, AuditEvent.Request_Sent, 'events.kafka',
            cid='cid-kafka-1', endpoint='orders', size=128, outcome=AuditOutcome.OK, duration_ms=3, data='{"order_id": 1}')

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.body.string_value, 'kafka-outgoing request-sent events.kafka ok')
        self.assertEqual(attributes[_column('endpoint')], 'orders')
        self.assertEqual(attributes[_column('size')], 128)

        self._assert_no_data_or_payload(attributes)

# ################################################################################################################################

    def test_mllp(self) -> 'None':

        message = 'MSH|^~\\&|HIS|HOSPITAL|LAB|LAB|20260301||ADT^A01|MSG-1|P|2.5\r'
        attrs = {'facility': 'HOSPITAL', 'message_type': 'ADT^A01', 'hl7_version': '2.5'}

        _ = audit_message_received(self.audit_log, 'adt.mllp', message, cid='cid-mllp-1', msg_id='MSG-1', attrs=attrs,
            endpoint='0.0.0.0:2575')

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.message-received')
        self.assertEqual(attributes[_column('source')], AuditSource.MLLP_Channel)
        self.assertEqual(attributes[_column('ext_client_id')], 'HOSPITAL')
        self.assertEqual(attributes[_column('msg_id')], 'MSG-1')
        self.assertEqual(attributes[_column('size')], len(message))

        self.assertEqual(attributes[_attr('facility')], 'HOSPITAL')
        self.assertEqual(attributes[_attr('message_type')], 'ADT^A01')
        self.assertEqual(attributes[_attr('hl7_version')], '2.5')

        self._assert_no_data_or_payload(attributes)

# ################################################################################################################################

    def test_alert_raised(self) -> 'None':

        rule = AlertRule()
        rule.name = 'crm-latency'

        finding = Finding()
        finding.kind = 'latency'
        finding.message = 'p95 latency 1,200 ms over 900 ms'
        finding.source = AuditSource.REST_Outgoing
        finding.object_name = 'crm.api'

        record_alert_event(self.audit_log, rule, finding, 3, 'cid-alert-1')

        record, attributes = _build_record(self.audit_log.last())

        self.assertEqual(record.event_name, 'zato.audit.alert-raised')
        self.assertEqual(attributes[_column('source')], AuditSource.REST_Outgoing)
        self.assertEqual(attributes[_column('object_name')], 'crm.api')

        # A source without a data allow list still sends the alert's keys
        self.assertEqual(attributes[_data('kind')], 'latency')
        self.assertEqual(attributes[_data('message')], 'p95 latency 1,200 ms over 900 ms')
        self.assertEqual(attributes[_data('rule')], 'crm-latency')
        self.assertEqual(attributes[_data('count')], 3)

# ################################################################################################################################
# ################################################################################################################################

class TestPayloadFlag(TestCase):

    def setUp(self) -> 'None':
        self.audit_log = CapturingAuditLog()

        self.request = '{"invoice_id": "INV-1", "amount": 100}'
        self.response = '{"status": "accepted"}'

        _ = self.audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, 'billing.invoices',
            cid='cid-flag-1', endpoint='/billing/invoices', size=22, outcome=AuditOutcome.OK, data=self.response,
            bodies={AuditBody.Request: self.request, AuditBody.Response: self.response})

        self.pending = self.audit_log.last()

# ################################################################################################################################

    def test_flag_off(self) -> 'None':

        _, attributes = _build_record(self.pending, is_payload_active=False)

        for name in attributes:
            self.assertFalse(name.startswith(DataCtx.Payload_Prefix), name)

        self.assertNotIn(DataCtx.Payload_Truncated, attributes)

# ################################################################################################################################

    def test_flag_on(self) -> 'None':

        _, attributes = _build_record(self.pending, is_payload_active=True)

        self.assertEqual(attributes[_payload('data')], self.response)
        self.assertEqual(attributes[_payload(AuditBody.Request)], self.request)
        self.assertEqual(attributes[_payload(AuditBody.Response)], self.response)
        self.assertNotIn(DataCtx.Payload_Truncated, attributes)

        # Columns are the same whatever the flag
        self.assertEqual(attributes[_column('endpoint')], '/billing/invoices')

# ################################################################################################################################

    def test_payload_name_per_body_kind(self) -> 'None':

        bodies = {
            AuditBody.Request: 'request-body',
            AuditBody.Response: 'response-body',
            AuditBody.Error: 'error-body',
            'sql-rows': '[{"id": 1}]',
        }

        _ = self.audit_log.insert(AuditSource.SQL_Outgoing, AuditEvent.Request_Sent, 'crm.db',
            cid='cid-flag-2', endpoint='crm.lookup', outcome=AuditOutcome.OK, bodies=bodies)

        _, attributes = _build_record(self.audit_log.last(), is_payload_active=True)

        self.assertEqual(attributes[_payload('request')], 'request-body')
        self.assertEqual(attributes[_payload('response')], 'response-body')
        self.assertEqual(attributes[_payload('error')], 'error-body')
        self.assertEqual(attributes[_payload('sql-rows')], '[{"id": 1}]')

        # SQL has a data allow list, so its data never goes as a payload
        self.assertNotIn(_payload('data'), attributes)

# ################################################################################################################################

    def test_size_cap_and_truncated_marker(self) -> 'None':

        max_size = 16

        _, attributes = _build_record(self.pending, is_payload_active=True, max_payload_size=max_size)

        self.assertEqual(attributes[_payload('data')], self.response[:max_size])
        self.assertEqual(attributes[_payload(AuditBody.Request)], self.request[:max_size])
        self.assertEqual(len(attributes[_payload(AuditBody.Request)]), max_size)
        self.assertIs(attributes[DataCtx.Payload_Truncated], True)

        # A cap no payload reaches leaves no marker
        _, attributes = _build_record(self.pending, is_payload_active=True, max_payload_size=1024)

        self.assertNotIn(DataCtx.Payload_Truncated, attributes)

# ################################################################################################################################

    def test_attachments_never_leave(self) -> 'None':

        _ = record_file_transfer(self.audit_log, 'reports.sftp', 'upload', '/outgoing/report.csv',
            cid='cid-flag-3', outcome=AuditOutcome.OK, size=5, content=b'a,b,c')

        _, attributes = _build_record(self.audit_log.last(), is_payload_active=True)

        self.assertNotIn('a,b,c', str(attributes))

        for name in attributes:
            self.assertFalse(name.startswith(DataCtx.Payload_Prefix), name)

# ################################################################################################################################

    def test_server_name_is_not_an_attribute(self) -> 'None':

        _, attributes = _build_record(self.pending, is_payload_active=True)

        self.assertEqual(self.pending.values['server_name'], Server_Name)
        self.assertNotIn(Server_Name, attributes.values())

# ################################################################################################################################
# ################################################################################################################################
