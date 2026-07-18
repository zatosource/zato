# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# Zato
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource

# Zato - test helpers
from conftest import wait_for_port_open
from test_mllp_audit import _build_adt_a01, _send_and_receive, _wait_for_events

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict
    any_ = any_
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

_connection_type_channel = 'channel-hl7-mllp'
_connection_type_outconn = 'outconn-hl7-mllp'
_connection_type_fhir    = 'outconn-hl7-fhir'
_generic_service_name    = 'zato.generic.connection'

# The names of everything this module creates
_channel_name         = 'test-mllp-services-accept'
_forward_channel_name = 'test-mllp-services-forward'
_fhir_outconn_name    = 'test-fhir-resend-outconn'

# The forward service deployed by the hot-deploy fixture sends through this exact name
_outconn_name = 'test-mllp-wire-outconn'

# The MSH-3 value routing messages to the forward channel
_forward_sender_application = 'FORWARDING_SYSTEM'

# The services the channels route to - deployed by the hot-deploy fixture
_channel_service_name = 'test.hl7.mllp.accept'

# How long to wait for routes and connection pools to settle after a create call
_settle_seconds = 1

# ################################################################################################################################
# ################################################################################################################################

def _invoke_report(zato_client:'any_', service_name:'str', payload:'anydict') -> 'anydict':
    """ Invokes an internal service that answers with a JSON report in response_data.
    """
    response = zato_client.invoke(service_name, payload)
    out = json.loads(response['response_data'])
    return out

# ################################################################################################################################
# ################################################################################################################################

class _FHIRPostHandler(BaseHTTPRequestHandler):
    """ A minimal FHIR server accepting resource writes - every POST echoes the resource back.
    """

    def do_POST(self) -> 'None':
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)

        self.send_response(201)
        self.send_header('Content-Type', 'application/fhir+json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()

        _ = self.wfile.write(body)

    def log_message(self, format:'str', *args:'any_') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class TestInternalServices:
    """ Live tests for the internal HL7 services - resend, reprocess, per-hop resend,
    parse-for-display, channel state and the channel bindings, all invoked
    through the admin API against a live server.
    """

    channel_id:'int' = 0
    forward_channel_id:'int' = 0
    outconn_id:'int' = 0
    fhir_outconn_id:'int' = 0

# ################################################################################################################################

    def test_01_create_connections(
        self,
        zato_client:'any_',
        mllp_port:'int',
        backend_port:'int',
        mllp_backend:'any_',
        ) -> 'None':
        """ Creates the audited channel, the audited outconn and the forward channel
        the resubmit tests run against.
        """

        # The audited default route - what the reprocess re-routes into
        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_channel_name,
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service=_channel_service_name,
            is_default=True,
            pool_size=1,
            is_audit_log_active=True,
        )

        assert 'id' in response
        self.__class__.channel_id = response['id']

        # The audited outconn pointing at the standalone backend - what the resend goes through
        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_outconn_name,
            type_=_connection_type_outconn,
            is_active=True,
            is_internal=False,
            is_channel=False,
            is_outconn=True,
            address=f'127.0.0.1:{backend_port}',
            pool_size=1,
            is_audit_log_active=True,
        )

        assert 'id' in response
        self.__class__.outconn_id = response['id']

        # The unaudited forward channel - it seeds the outconn's sent events
        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_forward_channel_name,
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.forward',
            msh3_sending_app=_forward_sender_application,
            pool_size=1,

            # The forward service needs the raw ER7 text
            should_parse_on_input=False,
        )

        assert 'id' in response
        self.__class__.forward_channel_id = response['id']

        wait_for_port_open(mllp_port)

        # The routes and connection pools settle asynchronously after the create calls return
        time.sleep(_settle_seconds)

# ################################################################################################################################

    def test_02_reprocess(self, zato_client:'any_', zato_server:'dict', mllp_port:'int') -> 'None':
        """ A stored inbound message flows through the channel's service again -
        the new attempt lands linked to the original by the correlation id.
        """
        audit_db_path = zato_server['audit_db_path']

        # One message through the channel produces the event the reprocess loads back ..
        message_bytes = _build_adt_a01('REPROCESS-SEED-001')
        ack_bytes = _send_and_receive('127.0.0.1', mllp_port, message_bytes)
        assert b'MSA|AA|REPROCESS-SEED-001' in ack_bytes

        received_events = _wait_for_events(audit_db_path, _channel_name, 1, AuditEvent.Message_Received)
        original = received_events[-1]

        # .. the reprocess re-routes the stored payload to the channel's service ..
        report = _invoke_report(zato_client, 'zato.audit-log.hl7.reprocess', {'event_id': original['id']})

        assert report['is_ok'], report
        assert report['control_id'] == 'REPROCESS-SEED-001', report
        assert report['service_name'] == _channel_service_name, report

        # .. and the new attempt is its own received event, linked to the original.
        received_events = _wait_for_events(audit_db_path, _channel_name, 2, AuditEvent.Message_Received)
        reprocessed = received_events[-1]

        assert reprocessed['id'] == report['event_id'], (reprocessed, report)
        assert reprocessed['correl_id'] == original['cid'], (reprocessed, original)
        assert reprocessed['msg_id'] == 'REPROCESS-SEED-001'
        assert reprocessed['outcome'] == AuditOutcome.OK

# ################################################################################################################################

    def test_03_resend(self, zato_client:'any_', zato_server:'dict', mllp_port:'int') -> 'None':
        """ A stored outbound message goes out again through the same outconn -
        the new attempt and its acknowledgment land linked to the original.
        """
        audit_db_path = zato_server['audit_db_path']

        # One message through the forward channel produces the sent event the resend loads back ..
        message_bytes = _build_adt_a01('RESEND-SEED-001', sender_application=_forward_sender_application)
        ack_bytes = _send_and_receive('127.0.0.1', mllp_port, message_bytes)
        assert b'MSA|AA|RESEND-SEED-001' in ack_bytes

        sent_events = _wait_for_events(audit_db_path, _outconn_name, 1, AuditEvent.Message_Sent)
        original = sent_events[-1]

        # .. the resend delivers the stored payload through the same outconn ..
        report = _invoke_report(zato_client, 'zato.audit-log.hl7.resend', {'event_id': original['id']})

        assert report['is_ok'], report
        assert report['control_id'] == 'RESEND-SEED-001', report
        assert report['ack_status'], report
        assert report['ack_outcome'] == AuditOutcome.OK, report

        # .. the new attempt is its own sent event, linked to the original ..
        sent_events = _wait_for_events(audit_db_path, _outconn_name, 2, AuditEvent.Message_Sent)
        resent = sent_events[-1]

        assert resent['id'] == report['event_id'], (resent, report)
        assert resent['correl_id'] == original['cid'], (resent, original)
        assert resent['msg_id'] == 'RESEND-SEED-001'

        # .. and the backend's acknowledgment landed on the resend's own cid.
        ack_events = _wait_for_events(audit_db_path, _outconn_name, 2, AuditEvent.Ack_Received)
        ack = ack_events[-1]

        assert ack['cid'] == resent['cid'], (ack, resent)
        assert ack['outcome'] == AuditOutcome.OK

# ################################################################################################################################

    def test_04_resend_with_edited_payload(self, zato_client:'any_', zato_server:'dict') -> 'None':
        """ An edited payload replaces the stored one on a resend - the new event
        is searchable by what the message says now.
        """
        audit_db_path = zato_server['audit_db_path']

        # The event test_03 seeded goes out again, this time with an edited control id ..
        sent_events = _wait_for_events(audit_db_path, _outconn_name, 1, AuditEvent.Message_Sent)
        original = sent_events[0]

        edited_payload = _build_adt_a01('RESEND-EDITED-001').decode('utf-8')

        report = _invoke_report(
            zato_client, 'zato.audit-log.hl7.resend',
            {'event_id': original['id'], 'payload': edited_payload})

        assert report['is_ok'], report
        assert report['control_id'] == 'RESEND-EDITED-001', report

        # .. and the new event carries the edited message's identity, not the original's.
        sent_events = _wait_for_events(audit_db_path, _outconn_name, 3, AuditEvent.Message_Sent)
        resent = sent_events[-1]

        assert resent['msg_id'] == 'RESEND-EDITED-001', resent
        assert resent['correl_id'] == original['cid'], (resent, original)

# ################################################################################################################################

    def test_05_parse_for_display(self, zato_client:'any_') -> 'None':
        """ An HL7 payload comes back as its display tree - parsed server-side
        over the generated model.
        """

        payload = _build_adt_a01('DISPLAY-001').decode('utf-8')

        report = _invoke_report(zato_client, 'zato.hl7.parse-for-display', {'data': payload})

        assert report['is_ok'], report

        tree = report['tree']
        assert tree['msg_type'] == 'ADT^A01', tree
        assert tree['control_id'] == 'DISPLAY-001', tree

        # The segments arrive in wire order, each with its labeled fields
        segment_ids = [segment['segment_id'] for segment in tree['segments']]
        assert segment_ids[0] == 'MSH', segment_ids
        assert 'PID' in segment_ids, segment_ids

        # A payload that does not parse comes back as a report, not an error -
        # the parser is deliberately tolerant, so only truly unreadable input fails
        report = _invoke_report(zato_client, 'zato.hl7.parse-for-display', {'data': ''})
        assert not report['is_ok']
        assert report['error']

# ################################################################################################################################

    def test_06_get_current_state(self, zato_client:'any_') -> 'None':
        """ The channel dashboard's counters come back per channel - received, acked
        and the listener's condition, straight from the in-process state.
        """

        report = _invoke_report(zato_client, 'zato.channel.hl7.get-current-state', {})

        states_by_name = {item['name']: item for item in report['channels']}
        assert _channel_name in states_by_name, sorted(states_by_name)

        # The earlier tests sent traffic through both channels this module created
        channel_state = states_by_name[_channel_name]
        assert channel_state['is_listening'] is True, channel_state
        assert channel_state['received'] >= 1, channel_state
        assert channel_state['acked'] >= 1, channel_state
        assert channel_state['nacked'] == 0, channel_state
        assert channel_state['last_message_time_iso'], channel_state

        forward_state = states_by_name[_forward_channel_name]
        assert forward_state['received'] >= 1, forward_state

        # An optional name narrows the response to one channel
        report = _invoke_report(
            zato_client, 'zato.channel.hl7.get-current-state', {'name': _channel_name})

        assert len(report['channels']) == 1, report
        assert report['channels'][0]['name'] == _channel_name

# ################################################################################################################################

    def test_07_channel_bindings(self, zato_client:'any_') -> 'None':
        """ The service-to-channel lookup covers HL7 MLLP channels - both through
        get-channel-list and through the IDE's binding list.
        """

        # The channel list needs the service's id first ..
        response = zato_client.invoke(
            'zato.service.get-by-name', {'cluster_id': 1, 'name': _channel_service_name})

        service_id = response['id']

        # .. the MLLP channels routing to the service come from the config manager ..
        response = zato_client.invoke(
            'zato.service.get-channel-list', {'id': service_id, 'channel_type': 'hl7-mllp'})

        channel_names = [item['name'] for item in response]
        assert _channel_name in channel_names, channel_names

        # .. and the IDE response carries the same binding for its mode selector.
        response = zato_client.invoke(
            'zato.service.ide.get-service', {'service_name': _channel_service_name})

        binding_list = response['current_service_binding_list']
        mllp_bindings = [item for item in binding_list if item['channel_type'] == 'hl7-mllp']

        binding_names = [item['name'] for item in mllp_bindings]
        assert _channel_name in binding_names, binding_list

# ################################################################################################################################

    def test_08_resend_hop_fhir(self, zato_client:'any_', zato_server:'dict') -> 'None':
        """ A recorded FHIR delivery is repeated through the same outconn -
        the per-hop resend of one hop to one destination.
        """
        audit_db_path = zato_server['audit_db_path']

        # A minimal FHIR server for the outconn to write to ..
        fhir_server = HTTPServer(('127.0.0.1', 0), _FHIRPostHandler)
        fhir_port = fhir_server.server_address[1]

        server_thread = threading.Thread(target=fhir_server.serve_forever, daemon=True)
        server_thread.start()

        try:

            # .. the audited FHIR outconn pointing at it ..
            response = zato_client.create(
                f'{_generic_service_name}.create',
                cluster_id=1,
                name=_fhir_outconn_name,
                type_=_connection_type_fhir,
                is_active=True,
                is_internal=False,
                is_channel=False,
                is_outconn=True,
                address=f'http://127.0.0.1:{fhir_port}',
                pool_size=1,
                is_audit_log_active=True,
            )

            assert 'id' in response
            self.__class__.fhir_outconn_id = response['id']

            # Wait for the connection pool to settle
            time.sleep(_settle_seconds)

            # .. one Patient write through the deployed service seeds the event ..
            _ = zato_client.invoke('test.hl7.fhir.save')

            request_events = _wait_for_events(
                audit_db_path, _fhir_outconn_name, 1, AuditEvent.Request_Sent)

            original = request_events[-1]
            assert original['source'] == AuditSource.FHIR

            # .. the per-hop resend repeats the exact same call ..
            report = _invoke_report(zato_client, 'zato.audit-log.resend-hop', {'event_id': original['id']})

            assert report['is_ok'], report

            # .. and the new attempt is its own request event, linked to the original.
            request_events = _wait_for_events(
                audit_db_path, _fhir_outconn_name, 2, AuditEvent.Request_Sent)

            resent = request_events[-1]
            assert resent['id'] == report['event_id'], (resent, report)
            assert resent['correl_id'] == original['cid'], (resent, original)
            assert resent['outcome'] == AuditOutcome.OK

        finally:
            fhir_server.shutdown()
            fhir_server.server_close()

# ################################################################################################################################

    def test_09_cleanup(self, zato_client:'any_') -> 'None':
        """ Deletes everything this module created, so the other test modules
        start from the same clean slate as before.
        """

        for connection_id in (
            self.__class__.forward_channel_id,
            self.__class__.channel_id,
            self.__class__.outconn_id,
            self.__class__.fhir_outconn_id,
        ):
            if connection_id:
                zato_client.delete(f'{_generic_service_name}.delete', id=connection_id)

# ################################################################################################################################
# ################################################################################################################################
