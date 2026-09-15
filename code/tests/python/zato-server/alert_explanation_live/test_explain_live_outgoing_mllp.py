# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The explain service end to end for an outgoing MLLP connection whose receiving system rejects every message - a
# real quickstart server, a real hl7apy MLLP receiver answering AR to everything it is sent, an outgoing connection
# with the audit log on pointing at it, imported through enmasse, real HL7 messages sent through the connection from
# a hot-deployed service the way a service of the server sends them, one real sweep, and the explained alert read off
# the server's own databases and received by a real SMTP receiver.

# stdlib
import os
from time import sleep, time

# SQLAlchemy
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import sessionmaker

# Zato
from zato.common.alerting.explain.evidence import Heading_Failures, Heading_Object
from zato.common.alerting.explain.settings_info import Label_Alerts, Off, On
from zato.common.alerting.explain.store import ExplanationStore
from zato.common.api import Alerting
from zato.common.audit_log.api import AuditEvent, AuditSource, event_table
from zato.common.defaults import default_cluster_id
from zato.common.hl7.mllp.reply import Rejection_Ack_Code
from zato.common.test.client import AdminClient

# Test helpers
from hl7_client.mllp_receiver import MLLPReceiver
from live_config import LiveServer
from live_enmasse import deactivate_document, import_document
from live_trace import Channel_Explain, Channel_Outgoing, Received, Sent, separator, trace
from test_explain_live import _assert_sound_explanation, _email_to, _trace_delivery
from test_explain_live_channel import _new_admin_client, _new_notification_config, _point_smtp_at_receiver, \
     _server_audit_engine, _unwrap

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

class TestExplainLiveOutgoingMLLP:

    def test_an_outgoing_mllp_connections_negative_acks_are_explained(
        self,
        ollama:'any_',
        zato_server:'any_',
        smtp_receiver:'any_',
        ) -> 'None':

        client = _new_admin_client()

        # The server's own notification connection delivers to the receiver ..
        _point_smtp_at_receiver(smtp_receiver)

        # .. the receiving system is a real hl7apy MLLP server turning every message away with an AR ..
        receiver = MLLPReceiver(ack_code=Rejection_Ack_Code)
        receiver.start()

        try:

            # .. and the connection with the audit log on points at it, with an ack threshold four messages go past.
            outgoing_document = _create_rejected_outgoing(receiver.address)

            # The sweep explains through the LLM connection and mails from the address below - as does the server's
            # own sweep job, which the suite's scheduler fires on its interval by now, and whichever of the two
            # reaches a fresh alert first, the other delivers with the explanation it stored.
            notification_config = _new_notification_config()

            # Real HL7 messages through the connection, from inside the server, each acknowledged with an AR
            _produce_rejects(client)

            # One real sweep inside the server - the collectors, the rules, the explain service and the delivery
            trace(Channel_Outgoing, Sent, f'invoke {Alerting.Service} with {notification_config}')
            _ = client.invoke(Alerting.Service, notification_config)

            # The receiver saw each message once ..
            assert len(receiver.deliveries) == _message_count

            # .. each acknowledgment is on record under the connection's name, the AR as what the MSA segment said ..
            acks = _get_acks_received()

            for row in acks:
                trace(Channel_Outgoing, Received, f'ack audit log: {row["event_time_iso"]} {row["application_outcome"]!r} '
                    f'{row["msg_id"]!r}')

            separator(Channel_Outgoing)

            assert len(acks) == _message_count

            for row in acks:
                assert row['application_outcome'] == Rejection_Ack_Code, row
                assert row['status'] == _reject_status, row

            # .. the acks fired the negative acks rule of the outgoing MLLP ruleset ..
            explanations = _get_stored_explanations()
            by_rule = {}

            for explanation in explanations:
                assert explanation['object_name'] == _conn_name
                assert explanation['source'] == AuditSource.MLLP_Outgoing
                by_rule[explanation['rule']] = explanation

            assert _negative_acks_rule in by_rule, sorted(by_rule)

            explained = by_rule[_negative_acks_rule]
            evidence = explained['evidence']

            # .. its Object is the connection's own, read from the generic connection row - where it sends,
            # whether over TLS, and the alert settings it sets of its own ..
            assert Heading_Object in evidence
            assert f'Name: {_conn_name}' in evidence
            assert 'Type: MLLP outgoing connection' in evidence
            assert f'Address: {receiver.address}' in evidence
            assert f'TLS: {Off}' in evidence
            assert f'Audit log: {On}' in evidence
            assert f'{Label_Alerts}: {On}' in evidence

            # .. the failures are the acks, one group under the reject text the connection read the AR as and the
            # code itself, all four of them counted ..
            assert Heading_Failures in evidence
            assert f'1. {_reject_status} - {Rejection_Ack_Code}' in evidence
            assert f'Count: {_message_count}' in evidence

            _assert_sound_explanation(explained, _reject_words)

            # .. the one remediation an outgoing connection's explanation may propose is a resubmit ..
            for explanation in explanations:
                if explanation['remediation'] is not None:
                    assert explanation['remediation']['action'] == Alerting.Remediation_Resubmit, explanation

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

            deactivate_document(outgoing_document)

        finally:
            receiver.stop()

# ################################################################################################################################
# ################################################################################################################################

# The connection of the proof and the system whose messages it sends
_conn_name = 'explain.live.outgoing.mllp'
_sending_application = 'EXPLAIN_LIVE_ADT'
_sending_facility = 'EXPLAIN_LIVE_HOSPITAL'

# How many messages go through and the threshold that many go past
_message_count = 4
_ack_threshold = 3

# The rule the acks fire, of the ruleset the outgoing MLLP connections are judged by
_negative_acks_rule = 'Negative_Acks'

# What the connection reads an AR as - the status each acknowledgment is on record with and the failures group under
_reject_status = f'Application reject ({Rejection_Ack_Code})'

# How long a connection just created may take to appear among the server's wrappers, and how often to look
_wrapper_wait_timeout = 60
_wrapper_wait_step = 0.5

# The words a sound explanation of a receiving system rejecting every message is expected to use at least one of
_reject_words = ['reject', 'receiv', 'remote', 'system', 'fail', 'error', 'negative', 'application']

# ################################################################################################################################
# ################################################################################################################################

def _create_rejected_outgoing(address:'str') -> 'anydict':
    """ The outgoing MLLP connection of the proof - pointing at the receiver, the audit log on, the LLM explaining
    its alerts, the default ack codes and a threshold low enough for four rejects to fire its rule. What is returned
    is the document it went in with, for the proof to deactivate it with once it is through.
    """
    out = {
        'outgoing_mllp': [{
            'name': _conn_name,
            'is_active': True,
            'address': address,
            'pool_size': 1,
            'is_audit_log_active': True,
            'alerts': {
                'is_active': True,
                'use_llm': True,
                'ack_threshold': _ack_threshold,
            },
        }],
    }

    import_document(out)

    trace(Channel_Outgoing, Sent, f'mllp connection `{_conn_name}` -> {address}')
    separator(Channel_Outgoing)

    return out

# ################################################################################################################################

def _build_adt_a01(control_id:'str') -> 'str':
    """ One ADT^A01 message the connection sends to the receiving system.
    """
    out = (
        f'MSH|^~\\&|{_sending_application}|{_sending_facility}|RECEIVER|RECEIVER|20260914120000||ADT^A01|{control_id}|P|2.5\r'
        f'EVN|A01|20260914120000\r'
        f'PID|||445566^^^{_sending_facility}^MR||SMITH^JOHN||19800101|M\r'
        f'PV1||I|ICU^Room1'
    )

    return out

# ################################################################################################################################

def _send_through(client:'AdminClient', message:'str') -> 'anydict':
    """ One message through the connection, from inside the server - a connection just created takes a moment to
    appear among the server's wrappers, so a send that finds nothing under the name yet is tried again.
    """
    payload = {'outconn': _conn_name, 'data': message}
    deadline = time() + _wrapper_wait_timeout

    while True:
        try:
            out = _unwrap(client.invoke(LiveServer.mllp_send_service, payload))
        except Exception:
            if time() < deadline:
                sleep(_wrapper_wait_step)
                continue
            raise
        else:
            return out

# ################################################################################################################################

def _produce_rejects(client:'AdminClient') -> 'None':
    """ Real HL7 messages through the connection - each reaches the receiver that turns everything away and comes
    back acknowledged with an AR, named on the trace with the code of its acknowledgment.
    """
    for index in range(_message_count):

        control_id = f'EXPLAIN-LIVE-OUT-{index + 1:03d}'

        trace(Channel_Outgoing, Sent, f'ADT^A01 {control_id} through `{_conn_name}`')

        response = _send_through(client, _build_adt_a01(control_id))
        ack_code = response['ack_code']

        trace(Channel_Outgoing, Received, f'{control_id} acknowledged {ack_code} - {response["ack_text"]!r}')
        separator(Channel_Outgoing)

        assert ack_code == Rejection_Ack_Code, response
        assert response['is_accepted'] is False, response
        assert control_id in response['ack_text'], response

# ################################################################################################################################

def _get_acks_received() -> 'anylist':
    """ Every acknowledgment the live connection received, as the server's audit log recorded it.
    """
    engine = _server_audit_engine()

    # The server creates the table with its first audit row, so until the first message lands there is nothing to read
    if not inspect(engine).has_table(event_table.name):
        return []

    query = select(event_table).\
        where(event_table.c.source == AuditSource.MLLP_Outgoing).\
        where(event_table.c.object_name == _conn_name).\
        where(event_table.c.event_type == AuditEvent.Ack_Received).\
        order_by(event_table.c.id)

    with engine.connect() as connection:
        out = [dict(row._mapping) for row in connection.execute(query)]

    return out

# ################################################################################################################################

def _get_stored_explanations() -> 'anylist':
    """ Every explanation the live server stored for the connection, read off its own ODB - the proofs share the
    server, so this one reads the explanations of its own connection alone.
    """
    path = os.path.join(os.path.dirname(LiveServer.server_directory), 'zato.db')
    session_maker = sessionmaker(bind=create_engine(f'sqlite:///{path}'))

    store = ExplanationStore(session_maker, default_cluster_id)

    # Our response to produce
    out:'anylist' = []

    for explanation in store.get_list():
        if explanation['source'] == AuditSource.MLLP_Outgoing:
            if explanation['object_name'] == _conn_name:
                out.append(explanation)

    for explanation in out:
        trace(Channel_Explain, Received, f'mllp outgoing {explanation["rule"]}: {explanation["explanation"]}')
        trace(Channel_Explain, Received, f'confidence: {explanation["confidence"]}, remediation: {explanation["remediation"]}')
        separator(Channel_Explain)

    return out

# ################################################################################################################################
# ################################################################################################################################
