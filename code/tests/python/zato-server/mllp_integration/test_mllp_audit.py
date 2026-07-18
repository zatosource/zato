# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import socket
import threading
import time
from base64 import b64encode
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, urlopen

# SQLAlchemy
from sqlalchemy import create_engine, select

# Zato
from zato.common.audit_log.api import event_attr_table, event_body_table, event_link_table, event_table, \
    AuditEvent, AuditLink, AuditOutcome, AuditSource
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode

# Zato - test helpers
from conftest import wait_for_port_open

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

# ################################################################################################################################
# ################################################################################################################################

_start_sequence   = b'\x0b'
_end_sequence     = b'\x1c\x0d'
_socket_timeout   = 5.0
_recv_buffer_size = 4096
_max_message_size = 2_000_000

_connection_type_channel = 'channel-hl7-mllp'
_connection_type_outconn = 'outconn-hl7-mllp'
_connection_type_fhir    = 'outconn-hl7-fhir'
_generic_service_name    = 'zato.generic.connection'
_http_soap_service_name  = 'zato.http-soap'

# MSH-3 values routing messages to the channels this module creates
_error_sender_application   = 'ERROR_SYSTEM'
_quiet_sender_application   = 'UNAUDITED_SYSTEM'
_forward_sender_application = 'FORWARDING_SYSTEM'

# The forward service sends through an outconn of this exact name
_forward_outconn_name = 'test-mllp-wire-outconn'

# The FHIR service invokes an outconn of this exact name
_fhir_outconn_name = 'test-fhir-audit-outconn'

# How long to wait for the server to write its audit rows after an ACK arrived
_audit_wait_seconds = 3.0

# ################################################################################################################################
# ################################################################################################################################

def _build_adt_a01(
    control_id:'str',
    sender_application:'str'='HIS',
    sender_facility:'str'='GENERAL_HOSPITAL',
    ) -> 'bytes':
    """ Builds a standard ADT^A01 message with an MR-typed patient identifier.
    """
    message = (
        f'MSH|^~\\&|{sender_application}|{sender_facility}|INTEGRATION_ENGINE|CENTRAL_HOSPITAL|'
        f'20260507120000||ADT^A01|{control_id}|P|2.5\r'
        f'EVN|A01|20260507120000\r'
        f'PID|||445566^^^GENERAL_HOSPITAL^MR||SMITH^JOHN||19800101|M\r'
        f'PV1||I|ICU^Room1'
    )

    out = message.encode('utf-8')
    return out

# ################################################################################################################################

def _build_batch(control_id_one:'str', control_id_two:'str') -> 'bytes':
    """ Builds a BHS batch with two ADT messages inside.
    """
    message = (
        f'BHS|^~\\&|HIS|GENERAL_HOSPITAL|INTEGRATION_ENGINE|CENTRAL_HOSPITAL|20260507120000\r'
        f'MSH|^~\\&|HIS|GENERAL_HOSPITAL|INTEGRATION_ENGINE|CENTRAL_HOSPITAL|'
        f'20260507120000||ADT^A01|{control_id_one}|P|2.5\r'
        f'EVN|A01|20260507120000\r'
        f'PID|||112233^^^GENERAL_HOSPITAL^MR||SMITH^ALICE||19800101|F\r'
        f'MSH|^~\\&|HIS|GENERAL_HOSPITAL|INTEGRATION_ENGINE|CENTRAL_HOSPITAL|'
        f'20260507120000||ADT^A03|{control_id_two}|P|2.5\r'
        f'EVN|A03|20260507120000\r'
        f'PID|||778899^^^GENERAL_HOSPITAL^MR||JONES^ROBERT||19900101|M\r'
        f'BTS|2'
    )

    out = message.encode('utf-8')
    return out

# ################################################################################################################################

def _send_and_receive(host:'str', port:'int', payload_bytes:'bytes') -> 'bytes':
    """ Opens a raw TCP socket, sends an MLLP-framed message, and reads the ACK response.
    """

    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_socket.settimeout(_socket_timeout)
    raw_socket.connect((host, port))

    try:

        framed_message = frame_encode(payload_bytes, _start_sequence, _end_sequence)
        raw_socket.sendall(framed_message)

        decoder = FrameDecoder(_start_sequence, _end_sequence, _max_message_size)

        while True:
            chunk = raw_socket.recv(_recv_buffer_size)

            if not chunk:
                raise Exception('Connection closed before receiving a complete ACK')

            decoder.feed(chunk)
            message = decoder.next_message()

            if message is not None:
                out = message
                break

        return out

    finally:
        raw_socket.close()

# ################################################################################################################################

def _send_rest(host:'str', port:'int', url_path:'str', payload_bytes:'bytes', password:'str') -> 'bytes':
    """ Sends an HL7 message via HTTP POST to a REST channel.
    """

    url = f'http://{host}:{port}{url_path}'
    auth = b64encode(f'admin.invoke:{password}'.encode()).decode()

    request = Request(url, data=payload_bytes, method='POST')
    request.add_header('Authorization', f'Basic {auth}')
    request.add_header('Content-Type', 'application/hl7-v2')

    with urlopen(request, timeout=_socket_timeout) as response:
        out = response.read()

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_events(audit_db_path:'str', object_name:'str', event_type:'str'='') -> 'anylist':
    """ Returns the audit events written for one object, oldest first, each as a dict.
    """

    engine = create_engine(f'sqlite:///{audit_db_path}')

    query = select(event_table)
    query = query.where(event_table.c.object_name == object_name)

    if event_type:
        query = query.where(event_table.c.event_type == event_type)

    query = query.order_by(event_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(dict(row._mapping))

    engine.dispose()
    return out

# ################################################################################################################################

def _get_attr_map(audit_db_path:'str', event_id:'int') -> 'anydict':
    """ Returns the attributes of one event as a dict of name to value.
    """

    engine = create_engine(f'sqlite:///{audit_db_path}')

    query = select(event_attr_table)
    query = query.where(event_attr_table.c.event_id == event_id)

    out:'anydict' = {}

    with engine.connect() as connection:
        for row in connection.execute(query):
            mapping = row._mapping
            out[mapping['name']] = mapping['value']

    engine.dispose()
    return out

# ################################################################################################################################

def _get_body_map(audit_db_path:'str', event_id:'int') -> 'anydict':
    """ Returns the bodies of one event as a dict of kind to data.
    """

    engine = create_engine(f'sqlite:///{audit_db_path}')

    query = select(event_body_table)
    query = query.where(event_body_table.c.event_id == event_id)

    out:'anydict' = {}

    with engine.connect() as connection:
        for row in connection.execute(query):
            mapping = row._mapping
            out[mapping['kind']] = mapping['data']

    engine.dispose()
    return out

# ################################################################################################################################

def _get_children(audit_db_path:'str', parent_event_id:'int', link_type:'str') -> 'anylist':
    """ Returns the child event ids linked to one parent, oldest first.
    """

    engine = create_engine(f'sqlite:///{audit_db_path}')

    query = select(event_link_table.c.child_event_id)
    query = query.where(event_link_table.c.parent_event_id == parent_event_id)
    query = query.where(event_link_table.c.link_type == link_type)
    query = query.order_by(event_link_table.c.child_event_id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(row[0])

    engine.dispose()
    return out

# ################################################################################################################################

def _wait_for_events(audit_db_path:'str', object_name:'str', expected_count:'int', event_type:'str'='') -> 'anylist':
    """ Polls until the expected number of events shows up for one object.
    """

    deadline = time.monotonic() + _audit_wait_seconds

    while time.monotonic() < deadline:

        out = _get_events(audit_db_path, object_name, event_type)

        if len(out) >= expected_count:
            return out

        time.sleep(0.1)

    out = _get_events(audit_db_path, object_name, event_type)
    return out

# ################################################################################################################################
# ################################################################################################################################

class _FHIRRequestHandler(BaseHTTPRequestHandler):
    """ A minimal FHIR server - every GET returns one Patient resource.
    """

    def do_GET(self) -> 'None':
        body = json.dumps({'resourceType': 'Patient', 'id': 'example'}).encode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/fhir+json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()

        _ = self.wfile.write(body)

    def log_message(self, format:'str', *args:'any_') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

class TestMLLPAudit:
    """ Wire-level tests for the HL7 audit producers running inside a live Zato server -
    the MLLP channel, the MLLP outconn, the HL7-over-REST re-tag, batch lineage
    and the FHIR outconn, all read back straight from the audit database.
    """

    accept_channel_id:'int' = 0
    error_channel_id:'int' = 0
    quiet_channel_id:'int' = 0
    forward_channel_id:'int' = 0
    outconn_id:'int' = 0
    rest_channel_id:'int' = 0
    fhir_outconn_id:'int' = 0

    rest_url_path:'str' = '/test/hl7/audit-rest'
    rest_channel_name:'str' = 'hl7.rest.test-audit'

# ################################################################################################################################

    def test_01_create_audited_channels(self, zato_client:'object', mllp_port:'int') -> 'None':
        """ Creates the channels this module runs against - an audited default route
        with parsing on, an audited error route and an unaudited quiet route.
        """

        # The audited default route - parsing is on, so the events carry parsed attributes
        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-mllp-audit-accept',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.accept',
            is_default=True,
            pool_size=1,
            is_audit_log_active=True,
        )

        assert 'id' in response
        self.__class__.accept_channel_id = response['id']

        # The audited error route - its service always raises
        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-mllp-audit-error',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.error',
            msh3_sending_app=_error_sender_application,
            pool_size=1,
            is_audit_log_active=True,
        )

        assert 'id' in response
        self.__class__.error_channel_id = response['id']

        # The unaudited quiet route - it must write nothing
        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-mllp-audit-quiet',
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.accept',
            msh3_sending_app=_quiet_sender_application,
            pool_size=1,
        )

        assert 'id' in response
        self.__class__.quiet_channel_id = response['id']

        wait_for_port_open(mllp_port)

# ################################################################################################################################

    def test_02_message_received_and_ack_sent(self, zato_server:'dict', mllp_port:'int') -> 'None':
        """ One accepted message writes a received event with parsed attributes
        and an ACK event, both on one cid.
        """
        audit_db_path = zato_server['audit_db_path']

        message_bytes = _build_adt_a01('AUDIT-001')
        ack_bytes = _send_and_receive('127.0.0.1', mllp_port, message_bytes)
        assert b'MSA|AA|AUDIT-001' in ack_bytes

        # The received event carries the message and its searchable attributes ..
        received_events = _wait_for_events(
            audit_db_path, 'test-mllp-audit-accept', 1, AuditEvent.Message_Received)

        received = received_events[-1]
        assert received['source'] == AuditSource.HL7
        assert received['msg_id'] == 'AUDIT-001'
        assert received['outcome'] == AuditOutcome.OK

        attrs = _get_attr_map(audit_db_path, received['id'])
        assert attrs['msg_type'] == 'ADT^A01', attrs
        assert attrs['mrn'] == '445566', attrs
        assert attrs['facility'] == 'GENERAL_HOSPITAL', attrs

        # .. the full message body is stored by reference ..
        bodies = _get_body_map(audit_db_path, received['id'])
        assert 'PID|||445566^^^GENERAL_HOSPITAL^MR||SMITH^JOHN' in bodies['request']

        # .. and the acknowledgment landed on the same cid, marked accepted.
        ack_events = _wait_for_events(
            audit_db_path, 'test-mllp-audit-accept', 1, AuditEvent.Ack_Sent)

        ack = ack_events[-1]
        assert ack['cid'] == received['cid']
        assert ack['msg_id'] == 'AUDIT-001'
        assert ack['outcome'] == AuditOutcome.OK

        ack_attrs = _get_attr_map(audit_db_path, ack['id'])
        assert ack_attrs['ack_status'] == 'AA', ack_attrs

# ################################################################################################################################

    def test_03_service_error_writes_negative_ack(self, zato_server:'dict', mllp_port:'int') -> 'None':
        """ A message whose service raises writes an ACK event that is an error of its own.
        """
        audit_db_path = zato_server['audit_db_path']

        message_bytes = _build_adt_a01('AUDIT-ERR-001', sender_application=_error_sender_application)
        ack_bytes = _send_and_receive('127.0.0.1', mllp_port, message_bytes)
        assert b'MSA|AE|AUDIT-ERR-001' in ack_bytes

        # The receipt itself succeeded ..
        received_events = _wait_for_events(
            audit_db_path, 'test-mllp-audit-error', 1, AuditEvent.Message_Received)
        assert received_events[-1]['outcome'] == AuditOutcome.OK

        # .. and the negative acknowledgment is a failure with its code on the row.
        ack_events = _wait_for_events(
            audit_db_path, 'test-mllp-audit-error', 1, AuditEvent.Ack_Sent)

        ack = ack_events[-1]
        assert ack['outcome'] == AuditOutcome.Error
        assert ack['application_outcome'] == 'AE'

# ################################################################################################################################

    def test_04_unaudited_channel_writes_nothing(self, zato_server:'dict', mllp_port:'int') -> 'None':
        """ A channel whose audit log is off leaves no trace in the audit database.
        """
        audit_db_path = zato_server['audit_db_path']

        message_bytes = _build_adt_a01('AUDIT-QUIET-001', sender_application=_quiet_sender_application)
        ack_bytes = _send_and_receive('127.0.0.1', mllp_port, message_bytes)
        assert b'MSA|AA|AUDIT-QUIET-001' in ack_bytes

        # Give any misdirected write time to land before asserting there is none
        time.sleep(1)

        events = _get_events(audit_db_path, 'test-mllp-audit-quiet')
        assert events == [], events

# ################################################################################################################################

    def test_05_batch_writes_parent_and_children(self, zato_server:'dict', mllp_port:'int') -> 'None':
        """ A BHS batch writes a parent event plus a child row per contained message,
        linked through the lineage table, each child with its own attributes.
        """
        audit_db_path = zato_server['audit_db_path']

        batch_bytes = _build_batch('BATCH-MSG-1', 'BATCH-MSG-2')
        ack_bytes = _send_and_receive('127.0.0.1', mllp_port, batch_bytes)
        assert b'MSA|AA|BATCH-MSG-1' in ack_bytes

        # The parent event describes the batch as a unit ..
        parent_events = _wait_for_events(
            audit_db_path, 'test-mllp-audit-accept', 1, AuditEvent.Interchange_Received)

        parent = parent_events[-1]
        parent_attrs = _get_attr_map(audit_db_path, parent['id'])
        assert parent_attrs['batch_count'] == '2', parent_attrs

        # .. the children hang off it through the lineage table ..
        child_ids = _get_children(audit_db_path, parent['id'], AuditLink.Batch_Item_Of)
        assert len(child_ids) == 2, child_ids

        # .. and each child carries its own control id and attributes.
        child_msg_ids = []

        for child_id in child_ids:

            child_events = [
                event for event in _get_events(audit_db_path, 'test-mllp-audit-accept', AuditEvent.Message_Received)
                if event['id'] == child_id
            ]

            child = child_events[0]
            assert child['cid'] == parent['cid']
            child_msg_ids.append(child['msg_id'])

        assert child_msg_ids == ['BATCH-MSG-1', 'BATCH-MSG-2'], child_msg_ids

        # The one acknowledgment covering the batch shares the parent's cid
        ack_events = _wait_for_events(
            audit_db_path, 'test-mllp-audit-accept', 1, AuditEvent.Ack_Sent)

        batch_acks = [event for event in ack_events if event['cid'] == parent['cid']]
        assert len(batch_acks) == 1, batch_acks

# ################################################################################################################################

    def test_06_outconn_writes_sent_and_ack_received(
        self,
        zato_client:'object',
        zato_server:'dict',
        mllp_port:'int',
        backend_port:'int',
        mllp_backend:'object',
        ) -> 'None':
        """ A message forwarded through an audited outconn writes a sent event
        and an ACK-received event, both on one cid.
        """
        audit_db_path = zato_server['audit_db_path']

        # The audited outconn pointing at the standalone backend ..
        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_forward_outconn_name,
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

        # .. an unaudited channel forwarding through it, so the outconn's own rows stand alone ..
        response = zato_client.create( # type: ignore[union-attr]
            f'{_generic_service_name}.create',
            cluster_id=1,
            name='test-mllp-audit-forward',
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

        # Wait for the route and the connection pool to settle
        time.sleep(1)

        # .. one message through the channel goes out through the outconn ..
        message_bytes = _build_adt_a01('AUDIT-FWD-001', sender_application=_forward_sender_application)
        ack_bytes = _send_and_receive('127.0.0.1', mllp_port, message_bytes)
        assert b'MSA|AA|AUDIT-FWD-001' in ack_bytes

        # .. the sent event carries the message and where it went ..
        sent_events = _wait_for_events(
            audit_db_path, _forward_outconn_name, 1, AuditEvent.Message_Sent)

        sent = sent_events[-1]
        assert sent['source'] == AuditSource.HL7
        assert sent['msg_id'] == 'AUDIT-FWD-001'
        assert sent['endpoint'] == f'127.0.0.1:{backend_port}'

        sent_attrs = _get_attr_map(audit_db_path, sent['id'])
        assert sent_attrs['msg_type'] == 'ADT^A01', sent_attrs

        # .. and the backend's acknowledgment landed on the same cid, marked accepted.
        ack_events = _wait_for_events(
            audit_db_path, _forward_outconn_name, 1, AuditEvent.Ack_Received)

        ack = ack_events[-1]
        assert ack['cid'] == sent['cid']
        assert ack['msg_id'] == 'AUDIT-FWD-001'
        assert ack['outcome'] == AuditOutcome.OK

# ################################################################################################################################

    def test_07_rest_channel_is_retagged_as_hl7(self, zato_client:'object', zato_server:'dict') -> 'None':
        """ HL7 arriving over REST is re-tagged at the writer - the events land
        as the HL7 source with HL7 fields, not as rest-channel noise.
        """
        audit_db_path = zato_server['audit_db_path']

        # An audited REST channel whose data format marks it as HL7 ..
        response = zato_client.create( # type: ignore[union-attr]
            f'{_http_soap_service_name}.create',
            cluster_id=1,
            name=self.__class__.rest_channel_name,
            is_active=True,
            is_internal=False,
            url_path=self.__class__.rest_url_path,
            connection='channel',
            transport='plain_http',
            service='test.hl7.mllp.echo',
            data_format='hl7-v2',
            match_slash=False,
            merge_url_params_req=True,
            is_audit_log_active=True,
        )

        assert 'id' in response
        self.__class__.rest_channel_id = response['id']

        # Wait for the channel to be picked up
        time.sleep(2)

        # .. one HL7 message over HTTP ..
        host     = zato_server['host']
        port     = zato_server['port']
        password = zato_server['password']

        message_bytes = _build_adt_a01('AUDIT-REST-001')
        _ = _send_rest(host, port, self.__class__.rest_url_path, message_bytes, password)

        # .. the request landed as an HL7 received event with HL7 fields ..
        received_events = _wait_for_events(
            audit_db_path, self.__class__.rest_channel_name, 1, AuditEvent.Message_Received)

        received = received_events[-1]
        assert received['source'] == AuditSource.HL7
        assert received['msg_id'] == 'AUDIT-REST-001'

        attrs = _get_attr_map(audit_db_path, received['id'])
        assert attrs['msg_type'] == 'ADT^A01', attrs
        assert attrs['facility'] == 'GENERAL_HOSPITAL', attrs

        # .. and the response landed as the acknowledgment answering it, on the same cid.
        ack_events = _wait_for_events(
            audit_db_path, self.__class__.rest_channel_name, 1, AuditEvent.Ack_Sent)

        ack = ack_events[-1]
        assert ack['source'] == AuditSource.HL7
        assert ack['cid'] == received['cid']

# ################################################################################################################################

    def test_08_fhir_outconn_writes_request_and_response(
        self,
        zato_client:'object',
        zato_server:'dict',
        ) -> 'None':
        """ A FHIR call through an audited outconn writes a request event
        and a response event, both on one cid, with the resource type searchable.
        """
        audit_db_path = zato_server['audit_db_path']

        # A minimal FHIR server for the outconn to talk to ..
        fhir_server = HTTPServer(('127.0.0.1', 0), _FHIRRequestHandler)
        fhir_port = fhir_server.server_address[1]

        server_thread = threading.Thread(target=fhir_server.serve_forever, daemon=True)
        server_thread.start()

        try:

            # .. the audited FHIR outconn pointing at it ..
            response = zato_client.create( # type: ignore[union-attr]
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
            time.sleep(1)

            # .. one Patient read through the deployed service ..
            _ = zato_client.invoke('test.hl7.fhir.invoke') # type: ignore[union-attr]

            # .. the request event says what was asked for ..
            request_events = _wait_for_events(
                audit_db_path, _fhir_outconn_name, 1, AuditEvent.Request_Sent)

            request = request_events[-1]
            assert request['source'] == AuditSource.FHIR
            assert request['endpoint'] == 'GET Patient/example'

            attrs = _get_attr_map(audit_db_path, request['id'])
            assert attrs['resource_type'] == 'Patient', attrs
            assert attrs['method'] == 'GET', attrs

            # .. and the response landed on the same cid, marked a success.
            response_events = _wait_for_events(
                audit_db_path, _fhir_outconn_name, 1, AuditEvent.Response_Received)

            fhir_response = response_events[-1]
            assert fhir_response['cid'] == request['cid']
            assert fhir_response['outcome'] == AuditOutcome.OK

        finally:
            fhir_server.shutdown()
            fhir_server.server_close()

# ################################################################################################################################

    def test_09_cleanup(self, zato_client:'object') -> 'None':
        """ Deletes everything this module created, so the other test modules
        start from the same clean slate as before.
        """

        for channel_id in (
            self.__class__.forward_channel_id,
            self.__class__.quiet_channel_id,
            self.__class__.error_channel_id,
            self.__class__.accept_channel_id,
            self.__class__.outconn_id,
            self.__class__.fhir_outconn_id,
        ):
            if channel_id:
                zato_client.delete(f'{_generic_service_name}.delete', id=channel_id) # type: ignore[union-attr]

        if self.__class__.rest_channel_id:
            zato_client.delete( # type: ignore[union-attr]
                f'{_http_soap_service_name}.delete', id=self.__class__.rest_channel_id)

# ################################################################################################################################
# ################################################################################################################################
