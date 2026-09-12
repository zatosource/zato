# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The details of one explanation - which LLM connection it goes through, which skill explains
# a probe's or a health check's alerts, what the Object section says of a file transfer
# connection and of one of its schedules, how the reply is read against the skill's
# remediations and what the stored explanation carries.

# stdlib
import json
import os

# Zato
from zato.common.alerting.collectors.common import Probe_Source_Test_Transfer
from zato.common.alerting.explain.evidence import Heading_Alert, Heading_Baseline, Heading_Failures, Heading_Object
from zato.common.alerting.explain.skill import Skill_File_Name, Skills_Dir_Name
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.alerting.model import AlertAction
from zato.common.alerting.object_config import storage_name, LLM_Connection_Config_Key
from zato.common.api import FileTransfer, GENERIC
from zato.common.audit_log.api import AuditEvent, AuditLog, AuditOutcome, AuditSource
from zato.common.odb.model import Cluster, GenericConn, HTTPBasicAuth, HTTPSOAP, Service

# Test helpers
from explain_helpers import _alert_id, _cluster_id, _conn_name, _error_data, _explanation_text, _llm_conn_name, _new_payload, \
    _new_service, _new_session, _seed_error_events, _server_name, _LLMFacade, LLMTestHandler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

# The object's own LLM connection, next to the deployment's default
_object_llm_conn_name = 'crm.own.llm'

# The file transfer connection and its schedule the Object section tests describe
_sftp_conn_name = 'partner.acme.sftp'
_schedule_name = 'acme.invoices.in'

# A skill header that lets the LLM propose restarting - what no shipped skill allows
_restart_skill = """---
name: rest-outgoing-explanation
description: A test skill
remediations: restart
---

# Restart skill

Explain the alert.
"""

# ################################################################################################################################
# ################################################################################################################################

def _seed_sftp_connection(session_maker:'any_', *, test_transfers:'bool'=False) -> 'None':
    """ One SFTP connection with a private key, host key checking off, one schedule and the test transfers toggle.
    """
    schedule = {
        'id': 'sched-1',
        'name': _schedule_name,
        'directory': '/outbox/invoices',
        'service': 'acme.invoices.handler',
        'run_every': 15,
        'run_unit': FileTransfer.Scheduler.Unit.Minutes,
        'is_active': True,
    }

    opaque = {
        'private_key': '/opt/zato/keys/acme_id_rsa',
        'strict_host_key_checking': False,
        FileTransfer.Scheduler.Schedules_Field: [schedule],
        storage_name('test_transfers'): test_transfers,
        storage_name('use_llm'): True,
    }

    row = GenericConn()
    row.name = _sftp_conn_name
    row.type_ = GENERIC.CONNECTION.TYPE.OUTCONN_SFTP
    row.is_active = True
    row.is_internal = False
    row.is_channel = False
    row.is_outconn = True
    row.address = 'sftp.acme.example.com:22'
    row.username = 'zato'
    row.secret = 'never-shown'
    row.cluster_id = _cluster_id
    row.opaque1 = json.dumps(opaque)

    session = session_maker()
    session.add(row)
    session.commit()
    session.close()

# ################################################################################################################################

def _stored_explanation(session_maker:'any_') -> 'dict':
    store = ExplanationStore(session_maker, _cluster_id)
    out = store.get(f'explanation.{_alert_id}')

    assert out is not None
    return out

# ################################################################################################################################

def _object_section(document:'str') -> 'str':
    start = document.index(Heading_Object)
    end = document.index(Heading_Failures)
    out = document[start:end]
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestWhichConnection:

    def test_the_objects_own_connection_wins_over_the_default(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_error_events()

        llm_connections = {
            _llm_conn_name: {'is_active': True},
            _object_llm_conn_name: {'is_active': True},
        }

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {LLM_Connection_Config_Key: _object_llm_conn_name}),
            session,
            repo_dir,
            llm=_LLMFacade(llm_connections, llm_address),
        )

        service.handle()

        assert service.llm.invoked_names == [_object_llm_conn_name]

# ################################################################################################################################

    def test_the_default_answers_when_the_object_names_none(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_error_events()

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        assert service.llm.invoked_names == [_llm_conn_name]

# ################################################################################################################################

    def test_no_connection_anywhere_stores_the_alert_unexplained(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_error_events()

        session = _new_session()
        payload = _new_payload(AlertAction.Email_Digest, {})
        payload['defaults']['llm_connection'] = ''

        service = _new_service(payload, session, repo_dir, llm=_LLMFacade({}, llm_address))

        service.handle()

        assert service.llm.invoked_names == []

        explanation = _stored_explanation(session)

        assert explanation['explanation'] == ''
        assert explanation['is_parsed'] is False

        # The evidence was still collected, so a person can read it
        assert _error_data in explanation['evidence']

# ################################################################################################################################

    def test_an_objects_connection_that_does_not_exist_means_none(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_error_events()

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {LLM_Connection_Config_Key: 'no.such.llm'}),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        # The object named a connection, so the default does not answer for it
        assert service.llm.invoked_names == []

# ################################################################################################################################
# ################################################################################################################################

class TestWhichSkill:

    def test_a_health_check_alert_is_explained_with_the_rest_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_error_events(AuditSource.REST_Outgoing_Health)

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}, AuditSource.REST_Outgoing_Health, measures=['health_state']),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        assert len(LLMTestHandler.prompts) == 1
        assert LLMTestHandler.prompts[0].startswith('# REST outgoing connection explanation')

        explanation = _stored_explanation(session)
        assert explanation['source'] == AuditSource.REST_Outgoing_Health

# ################################################################################################################################

    def test_a_test_transfer_alert_is_explained_with_the_file_transfer_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        audit_log = AuditLog(_server_name)

        _ = audit_log.insert(Probe_Source_Test_Transfer, AuditEvent.Run_Completed, _sftp_conn_name, cid='probe-1',
            outcome=AuditOutcome.Error, data='Permission denied')

        session = _new_session()
        _seed_sftp_connection(session, test_transfers=True)

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}, Probe_Source_Test_Transfer, object_name=_sftp_conn_name,
                measures=['test_transfer_failed']),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        assert len(LLMTestHandler.prompts) == 1

        prompt = LLMTestHandler.prompts[0]
        assert prompt.startswith('# File transfer connection explanation')

        # The probe row is the failure and the newest probe result is in the baseline
        assert '1. Permission denied' in prompt
        assert 'Test transfer result: error at' in prompt

# ################################################################################################################################

    def test_the_servers_own_skill_directory_is_read(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_error_events()

        skill_path = os.path.join(repo_dir, Skills_Dir_Name, AuditSource.REST_Outgoing, Skill_File_Name)

        with open(skill_path, 'w') as f:
            _ = f.write(_restart_skill)

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        assert LLMTestHandler.prompts[0].startswith('# Restart skill')

        # The shipped skill allows resubmit, this one does not - the reply's remediation is dropped
        explanation = _stored_explanation(session)

        assert explanation['explanation'] == _explanation_text
        assert explanation['is_parsed'] is True
        assert explanation['remediation'] is None

# ################################################################################################################################
# ################################################################################################################################

class TestObjectSection:

    def test_a_file_transfer_connection_is_described_without_its_secret(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_error_events(AuditSource.File_Outgoing, _sftp_conn_name)

        session = _new_session()
        _seed_sftp_connection(session)

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}, AuditSource.File_Outgoing, object_name=_sftp_conn_name),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        section = _object_section(LLMTestHandler.prompts[0])

        assert f'Name: {_sftp_conn_name}' in section
        assert 'Type: SFTP' in section
        assert 'Active: yes' in section
        assert 'Host: sftp.acme.example.com:22' in section
        assert 'Username: zato' in section
        assert 'Authentication: private key (/opt/zato/keys/acme_id_rsa), host key checking off' in section
        assert f'Schedule: {_schedule_name} - watches /outbox/invoices, delivers to acme.invoices.handler, ' + \
            'every 15 minutes, active' in section
        assert 'Test transfers: off' in section

        assert 'never-shown' not in LLMTestHandler.prompts[0]
        assert 'Schedule:' not in section.split('\n')[2]

# ################################################################################################################################

    def test_a_schedule_is_resolved_to_its_owning_connection(self, llm_address:'any_', repo_dir:'str') -> 'None':

        audit_log = AuditLog(_server_name)

        # A success under the connection - the baseline of a schedule reads under its owner
        _ = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Message_Sent, _sftp_conn_name, cid='ok-1',
            outcome=AuditOutcome.OK, endpoint='/outbox/INV-1.xml')

        # A failed run of the schedule, stored under the connection
        run_data = json.dumps({'schedule': _schedule_name, 'failed': 1})
        _ = audit_log.insert(AuditSource.File_Outgoing, AuditEvent.Run_Completed, _sftp_conn_name, cid='run-1',
            outcome=AuditOutcome.Error, status='failed', data=run_data)

        session = _new_session()
        _seed_sftp_connection(session, test_transfers=True)

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}, AuditSource.File_Outgoing, object_name=_schedule_name,
                measures=['runs_failed_in_window']),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        prompt = LLMTestHandler.prompts[0]
        section = _object_section(prompt)

        assert section.split('\n')[2] == f'Schedule: {_schedule_name}, of the SFTP connection {_sftp_conn_name}'
        assert f'Name: {_sftp_conn_name}' in section
        assert 'Test transfers: on' in section

        # The failed run is the failure, the connection's success is the baseline
        assert run_data in prompt
        assert 'OK events in the window: 1' in prompt
        assert 'Test transfer result: none on record yet' in prompt

# ################################################################################################################################

    def test_a_source_without_a_facade_contributes_its_name_alone(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_error_events(AuditSource.Scheduler)

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}, AuditSource.Scheduler),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        section = _object_section(LLMTestHandler.prompts[0])

        assert section.strip() == f'{Heading_Object}\n\nName: {_conn_name}'

# ################################################################################################################################

    def test_a_rest_connection_is_read_off_its_facade(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_error_events()

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        section = _object_section(LLMTestHandler.prompts[0])

        assert f'name: {_conn_name}' in section
        assert 'address_host: https://crm.example.com' in section
        assert 'timeout: 10' in section

# ################################################################################################################################
# ################################################################################################################################

class TestStoredExplanation:

    def test_the_document_and_the_reply_are_stored_together(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_error_events()

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        explanation = _stored_explanation(session)

        document = explanation['evidence']

        assert document == LLMTestHandler.prompts[0][-len(document):]

        for heading in (Heading_Alert, Heading_Object, Heading_Failures, Heading_Baseline):
            assert heading in document

        assert 'Measure: error_rate = 1, threshold error_rate_threshold = 0.5' in document
        assert explanation['remediation'] == {'action': 'resubmit'}
        assert explanation['confidence'] == 'high'
        assert explanation['created_iso'] != ''

# ################################################################################################################################
# ################################################################################################################################

# The REST channel the channel tests describe, the service behind it, the security definition its callers use
_channel_name = 'orders.api'
_channel_service_name = 'orders.get'
_channel_security_name = 'Partner API'

# ################################################################################################################################

def _seed_rest_channel(session_maker:'any_', *, with_security:'bool'=True) -> 'None':
    """ One REST channel with its service, a Basic Auth definition and alert settings of its own.
    """
    opaque = {
        'is_audit_log_active': True,
        storage_name('is_active'): True,
        storage_name('auth_failures'): 3,
        storage_name('use_llm'): True,
    }

    session = session_maker()
    cluster = session.query(Cluster).filter(Cluster.id==_cluster_id).one()

    service = Service(None, _channel_service_name, True, 'orders.OrdersGet', False, cluster)
    session.add(service)

    if with_security:
        security = HTTPBasicAuth(None, _channel_security_name, True, 'partner', 'Zato', 'never-shown', cluster)
        session.add(security)
    else:
        security = None

    row = HTTPSOAP()
    row.name = _channel_name
    row.is_active = True
    row.is_internal = False
    row.connection = 'channel'
    row.transport = 'plain_http'
    row.url_path = '/orders'
    row.method = 'POST'
    row.soap_action = ''
    row.data_format = 'json'
    row.service = service
    row.security = security
    row.cluster = cluster
    row.opaque1 = json.dumps(opaque)

    session.add(row)
    session.commit()
    session.close()

# ################################################################################################################################

def _seed_channel_failures() -> 'None':
    """ The calls a REST channel answered with an error - the request halves arrive fine, the responses
    carry the status and the caller.
    """
    audit_log = AuditLog(_server_name)

    for index in range(3):
        _ = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Request_Received, _channel_name, cid=f'call-{index}',
            outcome=AuditOutcome.OK, ext_client_id=_channel_security_name)
        _ = audit_log.insert(AuditSource.REST_Channel, AuditEvent.Response_Sent, _channel_name, cid=f'call-{index}',
            outcome=AuditOutcome.Error, status='401 Unauthorized', data='Invalid credentials',
            ext_client_id=_channel_security_name, endpoint=_channel_service_name)

# ################################################################################################################################
# ################################################################################################################################

class TestRestChannel:

    def test_a_rest_channel_alert_is_explained_with_the_rest_channel_skill(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_channel_failures()

        session = _new_session()
        _seed_rest_channel(session)

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}, AuditSource.REST_Channel, object_name=_channel_name,
                measures=['auth_failure_count']),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        assert len(LLMTestHandler.prompts) == 1

        prompt = LLMTestHandler.prompts[0]
        assert prompt.startswith('# REST channel explanation')

        # The channel's skill allows no remediation, so the reply's resubmit is dropped and the rest is kept
        explanation = _stored_explanation(session)

        assert explanation['source'] == AuditSource.REST_Channel
        assert explanation['explanation'] == _explanation_text
        assert explanation['is_parsed'] is True
        assert explanation['remediation'] is None

# ################################################################################################################################

    def test_the_object_section_describes_the_channel(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_channel_failures()

        session = _new_session()
        _seed_rest_channel(session)

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}, AuditSource.REST_Channel, object_name=_channel_name,
                measures=['auth_failure_count']),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        prompt = LLMTestHandler.prompts[0]
        section = _object_section(prompt)

        assert f'Name: {_channel_name}' in section
        assert 'Active: yes' in section
        assert 'URL path: /orders' in section
        assert 'Method: POST' in section
        assert f'Service: {_channel_service_name}' in section
        assert f'Security: {_channel_security_name} (Basic Auth)' in section
        assert 'Data format: json' in section
        assert 'Audit log: on' in section
        assert 'Alerts: on' in section
        assert 'Alert settings of its own: Auth failures 3' in section

        assert 'never-shown' not in prompt

        # The failures name the callers and the service, the baseline counts the responses
        assert '1. 401 Unauthorized - Invalid credentials' in prompt
        assert f'Service: {_channel_service_name}' in prompt
        assert f'Caller: {_channel_security_name}' in prompt
        assert 'OK events in the window: 0' in prompt

# ################################################################################################################################

    def test_a_channel_without_security_or_own_settings_says_so(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_channel_failures()

        session = _new_session()
        _seed_rest_channel(session, with_security=False)

        # The channel's own settings are the defaults
        with session() as s:
            row = s.query(HTTPSOAP).filter(HTTPSOAP.name==_channel_name).one()
            row.opaque1 = json.dumps({storage_name('is_active'): True})
            s.commit()

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}, AuditSource.REST_Channel, object_name=_channel_name,
                measures=['auth_failure_count']),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        section = _object_section(LLMTestHandler.prompts[0])

        assert 'Security: None' in section
        assert 'Alert settings of its own: none, the defaults apply' in section

# ################################################################################################################################

    def test_a_channel_that_is_not_in_the_odb_contributes_its_name_alone(self, llm_address:'any_', repo_dir:'str') -> 'None':

        _seed_channel_failures()

        session = _new_session()

        service = _new_service(
            _new_payload(AlertAction.Email_Digest, {}, AuditSource.REST_Channel, object_name=_channel_name,
                measures=['auth_failure_count']),
            session,
            repo_dir,
            llm=_LLMFacade({_llm_conn_name: {'is_active': True}}, llm_address),
        )

        service.handle()

        section = _object_section(LLMTestHandler.prompts[0])

        assert section.strip() == f'{Heading_Object}\n\nName: {_channel_name}'

# ################################################################################################################################
# ################################################################################################################################
