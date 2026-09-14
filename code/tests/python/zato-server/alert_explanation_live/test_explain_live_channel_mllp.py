# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explain service end to end for an MLLP channel whose service fails on every message - a real quickstart server
# with its MLLP listener on a port decided before it started, an MLLP channel with the audit log on in front of the
# service that raises, real HL7 messages sent over a socket the way a sending system sends them, each acknowledged
# negatively with an AR, one real sweep, and the explained alert read off the server's own databases and received by
# a real SMTP receiver.

# stdlib
import os
import socket
from time import sleep, time

# SQLAlchemy
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.explain.evidence import Heading_Failures, Heading_Object
from zato.common.alerting.explain.settings_info import Label_Alerts, On
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.api import Alerting, GENERIC
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.defaults import default_cluster_id
from zato.common.hl7.mllp.codec import FrameDecoder, frame_encode
from zato.common.hl7.mllp.reply import Rejection_Ack_Code
from zato.common.test.client import AdminClient

# Test helpers
from live_config import LiveServer
from live_trace import Channel_Channel, Channel_Explain, Received, Sent, separator, trace
from test_explain_live import _assert_sound_explanation, _email_to, _trace_delivery
from test_explain_live_channel import _find_by_name, _new_admin_client, _new_notification_config, _point_smtp_at_receiver, \
     _server_audit_engine, _unwrap

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist

# ################################################################################################################################
# ################################################################################################################################

class TestExplainLiveChannelMLLP:

    def test_an_mllp_channels_negative_acks_are_explained(
        self,
        ollama:'any_',
        zato_server:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        client = _new_admin_client()

        # The server's own notification connection delivers to the receiver ..
        _point_smtp_at_receiver(client, smtp_receiver)

        # .. and an MLLP channel with the audit log on takes every message from the sending application and hands
        # it to the service that fails on each, with an ack threshold four messages go past.
        channel_id = _create_reject_channel(client)

        # The sweep explains through the LLM connection and mails from the address below
        notification_config = _new_notification_config()

        # Real HL7 messages over a socket, each acknowledged with an AR
        _wait_for_listener()
        _produce_rejects()

        # One real sweep inside the server - the collectors, the rules, the explain service and the delivery
        trace(Channel_Channel, Sent, f'invoke {Alerting.Service} with {notification_config}')
        _ = client.invoke(Alerting.Service, notification_config)

        # Each acknowledgment is on record under the channel's name, the AR as what the MSA segment said ..
        acks = _get_acks_sent()

        for row in acks:
            trace(Channel_Channel, Received, f'ack audit log: {row["event_time_iso"]} {row["application_outcome"]!r} '
                f'{row["ext_client_id"]!r}')

        separator(Channel_Channel)

        assert len(acks) == _message_count

        for row in acks:
            assert row['application_outcome'] == Rejection_Ack_Code, row
            assert row['ext_client_id'] == _sending_facility, row

        # .. the acks fired the negative acks rule of the MLLP ruleset ..
        explanations = _get_stored_explanations()
        by_rule = {}

        for explanation in explanations:
            assert explanation['object_name'] == _channel_name
            assert explanation['source'] == AuditSource.MLLP_Channel
            by_rule[explanation['rule']] = explanation

        assert _negative_acks_rule in by_rule, sorted(by_rule)

        explained = by_rule[_negative_acks_rule]
        evidence = explained['evidence']

        # .. its Object is the channel's own, read from the generic connection row - the sending application it
        # matches on, the service and the alert settings it sets of its own ..
        assert Heading_Object in evidence
        assert f'Name: {_channel_name}' in evidence
        assert 'Type: MLLP channel' in evidence
        assert f'Match: MSH-3 = {_sending_application}' in evidence
        assert f'Service: {LiveServer.reject_service}' in evidence
        assert f'{Label_Alerts}: {On}' in evidence

        # .. the failures are the acks, grouped under the AR code, with the MSA segment of the acknowledgment itself
        # in the evidence and the sending facility as the caller ..
        assert Heading_Failures in evidence
        assert f'1. {Rejection_Ack_Code} - ' in evidence
        assert f'MSA|{Rejection_Ack_Code}|' in evidence
        assert _sending_facility in evidence

        _assert_sound_explanation(explained, _reject_words)

        # .. a channel's explanation never proposes a remediation ..
        for explanation in explanations:
            assert explanation['remediation'] is None, explanation

        # .. and the explained alert reached the mailbox.
        _trace_delivery(smtp_receiver)

        bodies = []
        for received in smtp_receiver.messages:
            assert received.recipients == _email_to
            bodies.append(received.body)

        for body in bodies:
            if explained['explanation'] in body:
                break
        else:
            raise AssertionError(f'Expected an email carrying {explained["explanation"]!r}')

        _ = client.delete('zato.generic.connection.delete', id=channel_id)

# ################################################################################################################################
# ################################################################################################################################

_mllp_type = GENERIC.CONNECTION.TYPE.CHANNEL_HL7_MLLP

# The channel of the proof and the sending system whose messages reach it
_channel_name = 'explain.live.channel.mllp'
_sending_application = 'EXPLAIN_LIVE_ADT'
_sending_facility = 'EXPLAIN_LIVE_HOSPITAL'

# How many messages go through and the threshold that many go past
_message_count = 4
_ack_threshold = 3

# The rule the acks fire, of the ruleset the MLLP channels are judged by
_negative_acks_rule = 'Negative_Acks'

# How MLLP frames a message on the wire and how long one exchange may take
_start_sequence = b'\x0b'
_end_sequence = b'\x1c\x0d'
_max_message_size = 2_000_000
_recv_buffer_size = 4096
_socket_timeout = 10.0

# How long to give the listener to accept connections and the routes to settle after the channel was created
_listener_wait_timeout = 60
_listener_wait_step = 0.2
_settle_seconds = 1

# The words a sound explanation of a service failing on every message is expected to use at least one of
_reject_words = ['reject', 'service', 'fail', 'error', 'handler', 'process', 'exception', 'negative']

# ################################################################################################################################
# ################################################################################################################################

def _create_reject_channel(client:'AdminClient') -> 'int':
    """ An MLLP channel of the live server matching one sending application, in front of the service that fails
    on every message - the audit log on, the LLM explaining its alerts, the sender told why each message failed,
    the default ack codes and a threshold low enough for four rejects to fire its rule.
    """
    existing = _find_by_name(client, 'zato.generic.connection.get-list', _channel_name)

    if existing is not None:
        return existing['id']

    response = _unwrap(client.create('zato.generic.connection.create',
        cluster_id=default_cluster_id,
        type_=_mllp_type,
        name=_channel_name,
        is_active=True,
        is_internal=False,
        is_channel=True,
        is_outconn=False,
        pool_size=1,
        service=LiveServer.reject_service,
        msh3_sending_app=_sending_application,
        should_return_errors=True,
        is_audit_log_active=True,
        alert_is_active=True,
        alert_use_llm=True,
        alert_ack_threshold=_ack_threshold,
    ))
    out = response['id']

    trace(Channel_Channel, Sent, f'mllp channel `{_channel_name}` MSH-3 = {_sending_application} -> {LiveServer.reject_service}')
    separator(Channel_Channel)

    return out

# ################################################################################################################################

def _wait_for_listener() -> 'None':
    """ Waits until the server's MLLP listener accepts connections and its routes settled after the channel was created.
    """
    deadline = time() + _listener_wait_timeout

    while True:
        try:
            with socket.create_connection((LiveServer.host, LiveServer.mllp_port), timeout=1):
                break
        except OSError:
            if time() > deadline:
                raise AssertionError(f'The MLLP listener did not answer on port {LiveServer.mllp_port} within {_listener_wait_timeout}s')
            sleep(_listener_wait_step)

    sleep(_settle_seconds)

# ################################################################################################################################

def _build_adt_a01(control_id:'str') -> 'bytes':
    """ One ADT^A01 message from the sending system the channel matches on.
    """
    message = (
        f'MSH|^~\\&|{_sending_application}|{_sending_facility}|ZATO|ZATO|20260914120000||ADT^A01|{control_id}|P|2.5\r'
        f'EVN|A01|20260914120000\r'
        f'PID|||445566^^^{_sending_facility}^MR||SMITH^JOHN||19800101|M\r'
        f'PV1||I|ICU^Room1'
    )

    out = message.encode('utf-8')
    return out

# ################################################################################################################################

def _send_and_receive(payload:'bytes') -> 'bytes':
    """ Opens a raw TCP socket to the listener, sends one MLLP-framed message and reads the acknowledgment.
    """
    raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    raw_socket.settimeout(_socket_timeout)
    raw_socket.connect((LiveServer.host, LiveServer.mllp_port))

    try:
        raw_socket.sendall(frame_encode(payload, _start_sequence, _end_sequence))

        decoder = FrameDecoder(_start_sequence, _end_sequence, _max_message_size)

        while True:
            chunk = raw_socket.recv(_recv_buffer_size)

            if not chunk:
                raise AssertionError('The connection closed before a complete acknowledgment arrived')

            decoder.feed(chunk)
            message = decoder.next_message()

            if message is not None:
                return message

    finally:
        raw_socket.close()

# ################################################################################################################################

def _produce_rejects() -> 'None':
    """ Real HL7 messages over the wire - each reaches the service that fails and comes back acknowledged with an AR,
    named on the trace with the code of its acknowledgment.
    """
    for index in range(_message_count):

        control_id = f'EXPLAIN-LIVE-{index + 1:03d}'

        trace(Channel_Channel, Sent, f'ADT^A01 {control_id} from {_sending_application} / {_sending_facility}')

        ack = _send_and_receive(_build_adt_a01(control_id))
        ack_text = ack.decode('utf-8')

        msa_line = [line for line in ack_text.split('\r') if line.startswith('MSA|')][0]
        ack_code = msa_line.split('|')[1]

        trace(Channel_Channel, Received, f'{control_id} acknowledged {ack_code} - {msa_line}')
        separator(Channel_Channel)

        assert ack_code == Rejection_Ack_Code, ack_text
        assert control_id in msa_line, ack_text

# ################################################################################################################################

def _get_acks_sent() -> 'anylist':
    """ Every acknowledgment the live channel sent, as the server's audit log recorded it.
    """
    engine = _server_audit_engine()

    # The server creates the table with its first audit row, so until the first message lands there is nothing to read
    if not inspect(engine).has_table(event_table.name):
        return []

    query = select(event_table).\
        where(event_table.c.source == AuditSource.MLLP_Channel).\
        where(event_table.c.object_name == _channel_name).\
        where(event_table.c.event_type == AuditEvent.Ack_Sent).\
        order_by(event_table.c.id)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################

def _get_stored_explanations() -> 'anylist':
    """ Every explanation the live server stored for the channel, read off its own ODB - the proofs share the
    server, so this one reads the explanations of its own channel alone.
    """
    path = os.path.join(os.path.dirname(LiveServer.server_directory), 'zato.db')
    session_maker = sessionmaker(bind=create_engine(f'sqlite:///{path}'))

    store = ExplanationStore(session_maker, default_cluster_id)

    # Our response to produce
    out:'anylist' = []

    for explanation in store.get_list():
        if explanation['source'] == AuditSource.MLLP_Channel:
            if explanation['object_name'] == _channel_name:
                out.append(explanation)

    for explanation in out:
        trace(Channel_Explain, Received, f'mllp {explanation["rule"]}: {explanation["explanation"]}')
        trace(Channel_Explain, Received, f'confidence: {explanation["confidence"]}, remediation: {explanation["remediation"]}')
        separator(Channel_Explain)

    return out

# ################################################################################################################################
# ################################################################################################################################
