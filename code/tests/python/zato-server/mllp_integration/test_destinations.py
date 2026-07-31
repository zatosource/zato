# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a live MLLP channel does with the destinations it declares - the message reaching each of
# them through the real outgoing connections, what a service says each of them is to receive, the
# acknowledgment a channel replying from a destination answers its sender with, a channel with no
# service at all, both delivery orders and a paused destination, every delivery read back
# from the audit database the server wrote it to.

# stdlib
import json
import socket
import socketserver
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# pytest
import pytest

# SQLAlchemy
from sqlalchemy import create_engine, select

# Zato
from zato.common.audit_log.api import event_attr_table, event_table, AuditEvent, AuditOutcome, AuditSource
from zato.common.destination.constants import DeliveryMode, DestinationType, Respond_From_Service
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode

# Zato - test helpers
from conftest import wait_for_port_open
from rest_echo_server import HTTPEchoHandler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Generator
    from zato.common.typing_ import any_, anydict, anylist
    any_ = any_
    anydict = anydict
    anylist = anylist

    echo_server_gen = Generator['_TrackingTCPServer', None, None]

# ################################################################################################################################
# ################################################################################################################################

_start_sequence   = b'\x0b'
_end_sequence     = b'\x1c\x0d'
_recv_buffer_size = 4096
_max_message_size = 2_000_000

# A destination the channel waits for may be tried more than once before it gives up,
# so the sender waits longer here than it does where every delivery goes through
_socket_timeout = 20.0

_connection_type_channel = 'channel-hl7-mllp'
_connection_type_outconn = 'outconn-hl7-mllp'
_connection_type_fhir    = 'outconn-hl7-fhir'
_generic_service_name    = 'zato.generic.connection'
_http_soap_service_name  = 'zato.http-soap'

# The channels this module runs against
_fanout_channel = 'test-destinations-fanout'
_reply_channel  = 'test-destinations-reply'
_dead_channel   = 'test-destinations-dead'
_plain_channel  = 'test-destinations-plain'
_order_channel  = 'test-destinations-order'

# The MSH-3 values routing a message to each of them
_fanout_sender = 'DESTINATIONS_FANOUT'
_reply_sender  = 'DESTINATIONS_REPLY'
_dead_sender   = 'DESTINATIONS_DEAD'
_plain_sender  = 'DESTINATIONS_PLAIN'
_order_sender  = 'DESTINATIONS_ORDER'

# The outgoing connections the destinations point at
_forward_outconn = 'test-destinations-outconn'
_reply_outconn   = 'test-destinations-reply-outconn'
_fhir_outconn    = 'test-destinations-fhir'
_dead_outconn    = 'test-destinations-dead-outconn'
_rest_outconn    = 'test-destinations-rest'

# The path the REST outgoing connection posts to on the echo server
_rest_url_path = '/hl7/admissions'

# The names the channels declare their destinations under - the service says what each of them
# receives by these very names
_forward_destination = 'forward-ehr'
_fhir_destination    = 'fhir-ehr'
_rest_destination    = 'rest-billing'
_second_destination  = 'forward-second'
_paused_destination  = 'paused-ehr'

# How long to wait for the server to write the rows of a fan-out it did not make its sender wait for
_audit_wait_seconds = 15.0

# What the reply-mode backend names itself as in MSH-3 of the acknowledgment it answers with -
# the same constant mllp_test_server.py builds that acknowledgment from
_reply_sending_application = 'MLLP_TEST_BACKEND'

# What the FHIR destination is sent, as the service builds it
_fhir_resource_id = 'from-the-service'

# The bodies the mock FHIR server was posted, oldest first
_fhir_bodies:'list[str]' = []

# ################################################################################################################################
# ################################################################################################################################

def _build_adt_a01(control_id:'str', sender_application:'str', note:'str'='') -> 'bytes':
    """ Builds an ADT^A01 routed by its sending application, with an optional note the service
    reads to learn what this message is for.
    """
    message = (
        f'MSH|^~\\&|{sender_application}|GENERAL_HOSPITAL|INTEGRATION_ENGINE|CENTRAL_HOSPITAL|'
        f'20260507120000||ADT^A01|{control_id}|P|2.5\r'
        f'EVN|A01|20260507120000\r'
        f'PID|||445566^^^GENERAL_HOSPITAL^MR||SMITH^JOHN||19800101|M'
    )

    if note:
        message = f'{message}\rNTE|1||{note}'

    out = message.encode('utf-8')
    return out

# ################################################################################################################################

def _send_and_receive(port:'int', payload_bytes:'bytes') -> 'bytes':
    """ Sends one MLLP-framed message and reads the acknowledgment it is answered with.
    """
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_socket.settimeout(_socket_timeout)
    raw_socket.connect(('127.0.0.1', port))

    try:
        framed_message = frame_encode(payload_bytes, _start_sequence, _end_sequence)
        raw_socket.sendall(framed_message)

        decoder = FrameDecoder(_start_sequence, _end_sequence, _max_message_size)

        while True:
            chunk = raw_socket.recv(_recv_buffer_size)

            if not chunk:
                raise Exception('Connection closed before receiving a complete acknowledgment')

            decoder.feed(chunk)
            message = decoder.next_message()

            if message is not None:
                out = message
                break

        return out

    finally:
        raw_socket.close()

# ################################################################################################################################

def _find_closed_port() -> 'int':
    """ Returns a port nothing listens on, which is what a destination that cannot be reached
    is pointed at.
    """
    temporary_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    temporary_socket.bind(('127.0.0.1', 0))

    _, port = temporary_socket.getsockname()

    temporary_socket.close()

    return port

# ################################################################################################################################
# ################################################################################################################################

def _new_destination(name:'str', destination_type:'str', connection:'str', **options:'any_') -> 'anydict':
    """ Returns one destination the way the Dashboard writes it into a channel's list.
    """
    out = {
        'name': name,
        'type': destination_type,
        'connection': connection,
        'is_active': options.pop('is_active', True),
        'options': options,
    }

    return out

# ################################################################################################################################

def _as_stored(destinations:'anylist') -> 'str':
    """ Returns a destination list in the form a channel stores it.
    """
    out = json.dumps(destinations)
    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_events(audit_db_path:'str', object_name:'str', event_type:'str', msg_id:'str'='') -> 'anylist':
    """ Returns the audit events one object recorded, oldest first, each as a dict.
    """
    engine = create_engine(f'sqlite:///{audit_db_path}')

    query = select(event_table)
    query = query.where(event_table.c.object_name == object_name)
    query = query.where(event_table.c.event_type == event_type)

    if msg_id:
        query = query.where(event_table.c.msg_id == msg_id)

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

def _get_message_cid(audit_db_path:'str', channel_name:'str', control_id:'str') -> 'str':
    """ Returns the correlation id one message was received under, which is what every delivery
    it fanned out to is recorded under as well.
    """
    deadline = time.monotonic() + _audit_wait_seconds

    while time.monotonic() < deadline:

        events = _get_events(audit_db_path, channel_name, AuditEvent.Message_Received, control_id)

        if events:
            out = events[-1]['cid']
            return out

        time.sleep(0.1)

    raise Exception(f'Channel `{channel_name}` did not record message `{control_id}` as received')

# ################################################################################################################################

def _get_hops(audit_db_path:'str', cid:'str') -> 'anylist':
    """ Returns every delivery recorded under one correlation id, oldest first.
    """
    engine = create_engine(f'sqlite:///{audit_db_path}')

    query = select(event_table)
    query = query.where(event_table.c.event_type == AuditEvent.Request_Sent)
    query = query.where(event_table.c.cid == cid)
    query = query.order_by(event_table.c.id)

    out:'anylist' = []

    with engine.connect() as connection:
        for row in connection.execute(query):
            out.append(dict(row._mapping))

    engine.dispose()
    return out

# ################################################################################################################################

def _wait_for_hops(audit_db_path:'str', cid:'str', expected_count:'int') -> 'anylist':
    """ Polls until one message has as many deliveries recorded as it is expected to have -
    the ones its sender did not wait for land after the acknowledgment already went out.
    """
    deadline = time.monotonic() + _audit_wait_seconds

    while time.monotonic() < deadline:

        out = _get_hops(audit_db_path, cid)

        if len(out) >= expected_count:
            return out

        time.sleep(0.1)

    out = _get_hops(audit_db_path, cid)
    return out

# ################################################################################################################################

def _get_details(row:'anydict') -> 'anydict':
    """ Returns what one delivery was recorded with - the payload that went out and whatever
    repeating that delivery needs.
    """
    out = json.loads(row['data'])
    return out

# ################################################################################################################################

def _get_hop_by_destination(rows:'anylist', audit_db_path:'str', destination_name:'str') -> 'anydict':
    """ Returns the delivery to one destination out of the deliveries of one message.
    """
    for row in rows:
        attrs = _get_attr_map(audit_db_path, row['id'])
        if attrs['destination_name'] == destination_name:
            out = row
            return out

    raise Exception(f'No delivery to `{destination_name}` among {len(rows)} recorded')

# ################################################################################################################################
# ################################################################################################################################

class _FHIRRequestHandler(BaseHTTPRequestHandler):
    """ A minimal FHIR server - it keeps what was posted to it and answers with a resource.
    """

    def do_POST(self) -> 'None':
        length = int(self.headers['Content-Length'])
        body = self.rfile.read(length).decode('utf-8')

        _fhir_bodies.append(body)

        payload = json.dumps({'resourceType': 'Patient', 'id': 'stored'}).encode('utf-8')

        self.send_response(201)
        self.send_header('Content-Type', 'application/fhir+json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()

        _ = self.wfile.write(payload)

    def log_message(self, format:'str', *args:'any_') -> 'None':
        pass

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def fhir_server() -> 'Generator[int, None, None]':
    """ Starts the FHIR server one of the destinations delivers to and returns the port it listens on.
    """
    server = HTTPServer(('127.0.0.1', 0), _FHIRRequestHandler)
    port = server.server_address[1]

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    yield port

    server.shutdown()
    server.server_close()

# ################################################################################################################################
# ################################################################################################################################

class _TrackingTCPServer(socketserver.TCPServer):
    """ A TCP server whose handler keeps the last request it was sent, which is where a test
    reads back what the REST destination delivered.
    """
    allow_reuse_address = True

    request_count = 0
    last_body = b''

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='module')
def rest_echo() -> 'echo_server_gen':
    """ Starts the HTTP echo server the REST destination delivers to and returns the server
    itself, its port and the requests it received both readable off it.
    """
    server = _TrackingTCPServer(('127.0.0.1', 0), HTTPEchoHandler)

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    yield server

    server.shutdown()
    server.server_close()

# ################################################################################################################################
# ################################################################################################################################

class TestChannelDestinations:
    """ Wire-level tests for what a channel's destinations receive, run against a live server.
    """

    fanout_channel_id:'int' = 0
    reply_channel_id:'int' = 0
    dead_channel_id:'int' = 0
    plain_channel_id:'int' = 0
    order_channel_id:'int' = 0

    forward_outconn_id:'int' = 0
    reply_outconn_id:'int' = 0
    fhir_outconn_id:'int' = 0
    dead_outconn_id:'int' = 0
    rest_outconn_id:'int' = 0

# ################################################################################################################################

    def test_01_create_the_connections_and_the_channels(
        self,
        zato_client:'any_',
        zato_server:'dict',
        mllp_port:'int',
        backend_port:'int',
        mllp_backend:'any_',
        reply_backend_port:'int',
        reply_backend:'any_',
        fhir_server:'int',
        rest_echo:'_TrackingTCPServer',
        ) -> 'None':
        """ Creates the outgoing connections the destinations point at and the channels
        that declare them.
        """

        # The connection the messages are forwarded through, pointing at the standalone backend ..
        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_forward_outconn,
            type_=_connection_type_outconn,
            is_active=True,
            is_internal=False,
            is_channel=False,
            is_outconn=True,
            address=f'127.0.0.1:{backend_port}',
            pool_size=1,
        )

        assert 'id' in response
        self.__class__.forward_outconn_id = response['id']

        # .. the connection to the backend that answers with an acknowledgment of its own, which is
        # what a channel replying from a destination has something to relay ..
        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_reply_outconn,
            type_=_connection_type_outconn,
            is_active=True,
            is_internal=False,
            is_channel=False,
            is_outconn=True,
            address=f'127.0.0.1:{reply_backend_port}',
            pool_size=1,
        )

        assert 'id' in response
        self.__class__.reply_outconn_id = response['id']

        # .. the connection nothing listens behind, so a delivery through it always fails - with
        # its own retries off, the engine's are the only ones a failing delivery goes through ..
        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_dead_outconn,
            type_=_connection_type_outconn,
            is_active=True,
            is_internal=False,
            is_channel=False,
            is_outconn=True,
            address=f'127.0.0.1:{_find_closed_port()}',
            pool_size=1,
            max_retries=0,
        )

        assert 'id' in response
        self.__class__.dead_outconn_id = response['id']

        # .. and the FHIR server one of the destinations writes a resource to ..
        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_fhir_outconn,
            type_=_connection_type_fhir,
            is_active=True,
            is_internal=False,
            is_channel=False,
            is_outconn=True,
            address=f'http://127.0.0.1:{fhir_server}',
            pool_size=1,
        )

        assert 'id' in response
        self.__class__.fhir_outconn_id = response['id']

        # .. the REST connection one of the destinations posts through, pointing at the echo server ..
        rest_echo_port = rest_echo.server_address[1]

        response = zato_client.create(
            f'{_http_soap_service_name}.create',
            cluster_id=1,
            name=_rest_outconn,
            is_active=True,
            is_internal=False,
            connection='outgoing',
            transport='plain_http',
            url_path=_rest_url_path,
            host=f'http://127.0.0.1:{rest_echo_port}',
        )

        assert 'id' in response
        self.__class__.rest_outconn_id = response['id']

        # .. the channel whose service says what two of its three destinations receive ..
        fanout_destinations = [
            _new_destination(_forward_destination, DestinationType.MLLP, _forward_outconn),
            _new_destination(_fhir_destination, DestinationType.FHIR, _fhir_outconn, method='POST', path='/Patient'),
            _new_destination(_rest_destination, DestinationType.REST, _rest_outconn, method='POST'),
        ]

        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_fanout_channel,
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.destinations',
            msh3_sending_app=_fanout_sender,
            pool_size=1,
            is_audit_log_active=True,
            should_parse_on_input=False,
            destinations=_as_stored(fanout_destinations),
            respond_from=Respond_From_Service,
            delivery_mode=DeliveryMode.Same_Time,
        )

        assert 'id' in response
        self.__class__.fanout_channel_id = response['id']

        # .. the channel that answers its sender with what its destination said ..
        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_reply_channel,
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.accept',
            msh3_sending_app=_reply_sender,
            pool_size=1,
            is_audit_log_active=True,
            should_parse_on_input=False,
            destinations=_as_stored([_new_destination(_forward_destination, DestinationType.MLLP, _reply_outconn)]),
            respond_from=_forward_destination,
        )

        assert 'id' in response
        self.__class__.reply_channel_id = response['id']

        # .. the channel whose only destination cannot be reached ..
        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_dead_channel,
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.accept',
            msh3_sending_app=_dead_sender,
            pool_size=1,
            is_audit_log_active=True,
            should_parse_on_input=False,
            destinations=_as_stored([_new_destination(_forward_destination, DestinationType.MLLP, _dead_outconn)]),
            respond_from=_forward_destination,
        )

        assert 'id' in response
        self.__class__.dead_channel_id = response['id']

        # .. the channel with no service of its own, which passes on what it accepts ..
        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_plain_channel,
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='',
            msh3_sending_app=_plain_sender,
            pool_size=1,
            is_audit_log_active=True,
            should_parse_on_input=False,
            destinations=_as_stored([_new_destination(_forward_destination, DestinationType.MLLP, _forward_outconn)]),
        )

        assert 'id' in response
        self.__class__.plain_channel_id = response['id']

        # .. and the channel that delivers to its destinations one after another, one of them paused.
        order_destinations = [
            _new_destination(_forward_destination, DestinationType.MLLP, _forward_outconn),
            _new_destination(_second_destination, DestinationType.MLLP, _forward_outconn),
            _new_destination(_paused_destination, DestinationType.MLLP, _dead_outconn, is_active=False),
        ]

        response = zato_client.create(
            f'{_generic_service_name}.create',
            cluster_id=1,
            name=_order_channel,
            type_=_connection_type_channel,
            is_active=True,
            is_internal=False,
            is_channel=True,
            is_outconn=False,
            service='test.hl7.mllp.accept',
            msh3_sending_app=_order_sender,
            pool_size=1,
            is_audit_log_active=True,
            should_parse_on_input=False,
            destinations=_as_stored(order_destinations),
            delivery_mode=DeliveryMode.In_Order,
        )

        assert 'id' in response
        self.__class__.order_channel_id = response['id']

        wait_for_port_open(mllp_port)

        # The routes and the connection pools register after the create calls return -
        # give the last of them a moment before the first message goes out.
        time.sleep(2)

# ################################################################################################################################

    def test_02_every_destination_of_a_channel_receives_the_message(
        self,
        zato_server:'dict',
        mllp_port:'int',
        rest_echo:'_TrackingTCPServer',
        ) -> 'None':
        """ One message fans out to all three destinations, each recorded as its own delivery
        under the correlation id the message arrived under.
        """
        audit_db_path = zato_server['audit_db_path']

        control_id = 'DEST-FANOUT-001'
        acknowledgment = _send_and_receive(mllp_port, _build_adt_a01(control_id, _fanout_sender))

        assert b'MSA|AA|' + control_id.encode() in acknowledgment

        cid = _get_message_cid(audit_db_path, _fanout_channel, control_id)
        hops = _wait_for_hops(audit_db_path, cid, 3)

        assert len(hops) == 3

        # The MLLP destination was sent the message as it arrived ..
        forward_hop = _get_hop_by_destination(hops, audit_db_path, _forward_destination)

        assert forward_hop['source'] == AuditSource.HL7
        assert forward_hop['object_name'] == _forward_outconn
        assert forward_hop['outcome'] == AuditOutcome.OK
        assert control_id in _get_details(forward_hop)['payload']

        # .. the FHIR destination was sent the resource the service built for it, at the path
        # the destination names ..
        fhir_hop = _get_hop_by_destination(hops, audit_db_path, _fhir_destination)

        assert fhir_hop['source'] == AuditSource.FHIR
        assert fhir_hop['object_name'] == _fhir_outconn
        assert fhir_hop['outcome'] == AuditOutcome.OK

        fhir_details = _get_details(fhir_hop)

        assert _fhir_resource_id in fhir_details['payload']
        assert fhir_details['method'] == 'POST'
        assert fhir_details['path'] == '/Patient'

        # .. the REST destination was posted the message as it arrived ..
        rest_hop = _get_hop_by_destination(hops, audit_db_path, _rest_destination)

        assert rest_hop['source'] == AuditSource.REST_Outgoing
        assert rest_hop['object_name'] == _rest_outconn
        assert rest_hop['outcome'] == AuditOutcome.OK
        assert control_id in _get_details(rest_hop)['payload']

        # .. each delivery says which destination of which channel it was, and that it took
        # one attempt ..
        forward_attrs = _get_attr_map(audit_db_path, forward_hop['id'])

        assert forward_attrs['channel_name'] == _fanout_channel
        assert forward_attrs['destination_type'] == DestinationType.MLLP
        assert forward_attrs['attempt'] == '1'

        # .. the FHIR server really was written to ..
        assert any(_fhir_resource_id in item for item in _fhir_bodies)

        # .. and so was the echo server behind the REST destination.
        assert rest_echo.request_count >= 1
        assert control_id.encode() in rest_echo.last_body

# ################################################################################################################################

    def test_03_what_the_service_said_reaches_every_destination(
        self,
        zato_server:'dict',
        mllp_port:'int',
        ) -> 'None':
        """ A service that sets one payload for all of its channel's destinations has it delivered
        to each of them, except where it named one of them separately.
        """
        audit_db_path = zato_server['audit_db_path']

        control_id = 'DEST-FANOUT-002'
        _ = _send_and_receive(mllp_port, _build_adt_a01(control_id, _fanout_sender, note='BROADCAST'))

        cid = _get_message_cid(audit_db_path, _fanout_channel, control_id)
        hops = _wait_for_hops(audit_db_path, cid, 3)

        # What the service made of the message is what went out ..
        forward_hop = _get_hop_by_destination(hops, audit_db_path, _forward_destination)

        assert 'Seen by the service' in _get_details(forward_hop)['payload']

        # .. the REST destination received the same broadcast ..
        rest_hop = _get_hop_by_destination(hops, audit_db_path, _rest_destination)

        assert 'Seen by the service' in _get_details(rest_hop)['payload']

        # .. and the destination the service named separately still received what it was named with.
        fhir_hop = _get_hop_by_destination(hops, audit_db_path, _fhir_destination)

        assert _fhir_resource_id in _get_details(fhir_hop)['payload']
        assert 'Seen by the service' not in _get_details(fhir_hop)['payload']

# ################################################################################################################################

    def test_04_one_destination_may_receive_something_of_its_own(
        self,
        zato_server:'dict',
        mllp_port:'int',
        ) -> 'None':
        """ A service naming one destination has that destination alone receive what it was
        named with, the others receiving the message as it arrived.
        """
        audit_db_path = zato_server['audit_db_path']

        control_id = 'DEST-FANOUT-003'
        _ = _send_and_receive(mllp_port, _build_adt_a01(control_id, _fanout_sender, note='PER_NAME'))

        cid = _get_message_cid(audit_db_path, _fanout_channel, control_id)
        hops = _wait_for_hops(audit_db_path, cid, 3)

        forward_hop = _get_hop_by_destination(hops, audit_db_path, _forward_destination)

        assert 'For the EHR alone' in _get_details(forward_hop)['payload']

        # The destination named separately was the only one to receive that payload
        rest_hop = _get_hop_by_destination(hops, audit_db_path, _rest_destination)

        assert 'For the EHR alone' not in _get_details(rest_hop)['payload']

# ################################################################################################################################

    def test_05_a_destination_the_service_dropped_receives_nothing(
        self,
        zato_server:'dict',
        mllp_port:'int',
        ) -> 'None':
        """ A destination the service dropped for one message is not delivered to at all,
        and leaves no row behind for that message.
        """
        audit_db_path = zato_server['audit_db_path']

        control_id = 'DEST-FANOUT-004'
        _ = _send_and_receive(mllp_port, _build_adt_a01(control_id, _fanout_sender, note='DROPPED'))

        cid = _get_message_cid(audit_db_path, _fanout_channel, control_id)
        hops = _wait_for_hops(audit_db_path, cid, 2)

        # Give the delivery that must not happen the same chance to land as the ones that must
        time.sleep(1)

        hops = _get_hops(audit_db_path, cid)

        assert len(hops) == 2

        names = set()

        for row in hops:
            attrs = _get_attr_map(audit_db_path, row['id'])
            names.add(attrs['destination_name'])

        assert names == {_fhir_destination, _rest_destination}

# ################################################################################################################################

    def test_06_the_destination_a_channel_replies_from_answers_the_sender(
        self,
        zato_server:'dict',
        mllp_port:'int',
        ) -> 'None':
        """ A channel that replies from one of its destinations answers its sender with the
        acknowledgment that destination answered the delivery with.
        """
        audit_db_path = zato_server['audit_db_path']

        control_id = 'DEST-REPLY-001'
        acknowledgment = _send_and_receive(mllp_port, _build_adt_a01(control_id, _reply_sender))

        # The backend names itself in the acknowledgment it builds, so the sender being answered
        # with that name is the destination's own answer having been relayed rather than one
        # the channel built for itself
        assert _reply_sending_application.encode() in acknowledgment
        assert b'MSA|AA|' + control_id.encode() in acknowledgment

        cid = _get_message_cid(audit_db_path, _reply_channel, control_id)
        hops = _wait_for_hops(audit_db_path, cid, 1)

        assert len(hops) == 1
        assert hops[0]['object_name'] == _reply_outconn
        assert hops[0]['outcome'] == AuditOutcome.OK

# ################################################################################################################################

    def test_07_a_destination_that_cannot_be_reached_is_tried_again_and_then_said_so(
        self,
        zato_server:'dict',
        mllp_port:'int',
        ) -> 'None':
        """ A destination the channel replies from failing is the channel's own failure - the
        sender is told so, and every attempt at that destination is a row of its own.
        """
        audit_db_path = zato_server['audit_db_path']

        control_id = 'DEST-DEAD-001'
        acknowledgment = _send_and_receive(mllp_port, _build_adt_a01(control_id, _dead_sender))

        assert b'MSA|AE|' + control_id.encode() in acknowledgment

        cid = _get_message_cid(audit_db_path, _dead_channel, control_id)
        hops = _wait_for_hops(audit_db_path, cid, 3)

        # The first attempt and the two it is allowed after it are all recorded, so a delivery
        # that never got through is a row somebody can act on
        assert len(hops) == 3

        attempts = []

        for row in hops:
            assert row['outcome'] == AuditOutcome.Error
            assert row['status']
            attempts.append(_get_attr_map(audit_db_path, row['id'])['attempt'])

        assert attempts == ['1', '2', '3']

# ################################################################################################################################

    def test_08_a_channel_with_no_service_passes_the_message_on(
        self,
        zato_server:'dict',
        mllp_port:'int',
        ) -> 'None':
        """ A channel that names no service delivers what it accepts to its destinations itself,
        the message going out as it arrived.
        """
        audit_db_path = zato_server['audit_db_path']

        control_id = 'DEST-PLAIN-001'
        message_bytes = _build_adt_a01(control_id, _plain_sender)
        acknowledgment = _send_and_receive(mllp_port, message_bytes)

        assert b'MSA|AA|' + control_id.encode() in acknowledgment

        cid = _get_message_cid(audit_db_path, _plain_channel, control_id)
        hops = _wait_for_hops(audit_db_path, cid, 1)

        assert len(hops) == 1
        assert hops[0]['outcome'] == AuditOutcome.OK

        details = _get_details(hops[0])

        assert details['payload'] == message_bytes.decode('utf-8')

# ################################################################################################################################

    def test_09_delivering_one_after_another_keeps_the_order_and_skips_what_is_paused(
        self,
        zato_server:'dict',
        mllp_port:'int',
        ) -> 'None':
        """ A channel delivering one after another reaches its destinations in the order it
        declares them, and a paused destination is not delivered to at all.
        """
        audit_db_path = zato_server['audit_db_path']

        control_id = 'DEST-ORDER-001'
        acknowledgment = _send_and_receive(mllp_port, _build_adt_a01(control_id, _order_sender))

        assert b'MSA|AA|' + control_id.encode() in acknowledgment

        cid = _get_message_cid(audit_db_path, _order_channel, control_id)
        hops = _wait_for_hops(audit_db_path, cid, 2)

        # Give the paused destination the same chance to be delivered to as the other two
        time.sleep(1)

        hops = _get_hops(audit_db_path, cid)

        assert len(hops) == 2

        names = []
        sequences = []

        for row in hops:
            attrs = _get_attr_map(audit_db_path, row['id'])
            names.append(attrs['destination_name'])
            sequences.append(attrs['delivery_sequence'])

        assert names == [_forward_destination, _second_destination]
        assert sequences == ['0', '1']

# ################################################################################################################################

    def test_10_cleanup(self, zato_client:'any_') -> 'None':
        """ Deletes everything this module created, so the other test modules start from the
        same clean slate as before.
        """
        for connection_id in (
            self.__class__.fanout_channel_id,
            self.__class__.reply_channel_id,
            self.__class__.dead_channel_id,
            self.__class__.plain_channel_id,
            self.__class__.order_channel_id,
            self.__class__.forward_outconn_id,
            self.__class__.reply_outconn_id,
            self.__class__.fhir_outconn_id,
            self.__class__.dead_outconn_id,
        ):
            if connection_id:
                zato_client.delete(f'{_generic_service_name}.delete', id=connection_id)

        # The REST connection is not a generic one and is deleted through its own service
        if self.__class__.rest_outconn_id:
            zato_client.delete(f'{_http_soap_service_name}.delete', id=self.__class__.rest_outconn_id)

# ################################################################################################################################
# ################################################################################################################################
