# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the writer runs under gevent as in the server, so the patching runs before anything else is imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import json
import os
import ssl
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(__file__))

# gevent
from gevent import joinall, spawn

# SQLAlchemy
from sqlalchemy import event as sa_event

# Zato
from live_db import Line_Claimed, Line_Committing, Line_Delivered, Line_Ready, new_audit_log, new_event
from zato.common.audit_log.api import AuditSource, get_audit_engine
from zato.common.b2b.common.address_state import AddressRegistry, is_transport_error
from zato.common.b2b.common.clock import ManualClock, SystemClock
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.commit_sql import ClaimWrite
from zato.common.b2b.common.send_log import SendLog
from zato.common.b2b.common.store import MessageStore
from zato.common.test.b2b_cpa import new_settings
from zato.common.test.b2b_ebms2 import deliver, new_exchange, new_payload, send, Start_Time, use_store
from zato.common.test.b2b_pki import rsa_parties
from zato.common.test.b2b_write_path import new_identity, new_sent_message, new_stored_message, Server, Source, \
    Start_Time as Write_Path_Start_Time

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, strlist
    any_ = any_
    anylist = anylist
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# How long the writer of a child waits between two commits, in milliseconds.
_interval_ms = 10

# A row limit that no transaction of a child reaches.
_max_rows = 1_000_000

# How long a child that is to be stopped waits for its signal, in seconds.
_wait_for_kill_seconds = 3600

# How long one request of a child waits for its response, in seconds.
_request_timeout_seconds = 10

# ################################################################################################################################
# ################################################################################################################################

def write_events(batches:'int', batch_size:'int') -> 'None':
    """ Commits batches of events, each with its attribute and body, while the parent commits its own.
    """
    engine = get_audit_engine()
    writer = GroupCommitWriter(engine, interval_ms=0, max_rows=_max_rows, is_started=False)
    audit_log = new_audit_log()

    print(Line_Ready, flush=True)

    count = 0

    for batch_idx in range(batches):
        for idx in range(batch_size):
            _ = writer.enqueue(new_event(audit_log, f'child-{batch_idx}-{idx}'), 3)
            count += 1

        _ = writer.commit_due()

    print(json.dumps({'events': count}), flush=True)

# ################################################################################################################################

def claim_shared(start_at:'float', count:'int') -> 'None':
    """ Claims the shared identities from the moment both processes agreed on, and reports which it claimed.
    """
    engine = get_audit_engine()
    writer = GroupCommitWriter(engine, interval_ms=_interval_ms)

    tickets:'anylist' = []

    delay = start_at - time.time()
    if delay > 0:
        time.sleep(delay)

    for idx in range(count):
        write = ClaimWrite()
        write.identity = new_identity(f'shared-{idx}')
        write.message = new_stored_message()

        ticket = writer.submit(write, 1)
        tickets.append(ticket)

    claimed:'strlist' = []

    for idx, ticket in enumerate(tickets):
        if ticket.wait():
            claimed.append(f'shared-{idx}')

    writer.stop()

    print(json.dumps({'claimed': claimed}), flush=True)

# ################################################################################################################################

def kill_before_commit(message_id:'str') -> 'None':
    """ Claims a message and waits to be stopped while the commit of the claim has not completed.
    """
    engine = get_audit_engine()
    writer = GroupCommitWriter(engine, interval_ms=_interval_ms)
    store = MessageStore(writer)

    def on_commit(conn:'any_') -> 'None':
        print(Line_Committing, flush=True)
        time.sleep(_wait_for_kill_seconds)

    sa_event.listen(engine, 'commit', on_commit)

    _ = store.claim(new_identity(message_id), new_stored_message())

# ################################################################################################################################

def kill_after_commit(message_id:'str') -> 'None':
    """ Claims a message and waits to be stopped before the acknowledgment of the message would be sent.
    """
    engine = get_audit_engine()
    writer = GroupCommitWriter(engine, interval_ms=_interval_ms)
    store = MessageStore(writer)

    _ = store.claim(new_identity(message_id), new_stored_message())

    print(Line_Claimed, flush=True)
    time.sleep(_wait_for_kill_seconds)

def kill_before_confirm(payload_text:'str') -> 'None':
    """ Receives a message whose delivery commits, reports its MessageId, and waits to be stopped
    before the application confirms the delivery.
    """
    engine = get_audit_engine()
    writer = GroupCommitWriter(engine, interval_ms=_interval_ms)

    parties = rsa_parties()
    settings = new_settings(parties, Start_Time)

    exchange = new_exchange(parties, settings)
    use_store(exchange.receiver, MessageStore(writer))

    payload = new_payload(payload_text.encode('utf8'))
    outbound = send(exchange, [payload])

    result = deliver(exchange, outbound)
    delivery = result.deliveries[0]

    print(json.dumps({'message_id': delivery.message_id}), flush=True)
    print(Line_Delivered, flush=True)

    time.sleep(_wait_for_kill_seconds)

def seed_open(count:'int', batch_size:'int') -> 'None':
    """ Records the first deliveries of messages whose exchanges stay open, many at a time, and reports how many.
    """
    engine = get_audit_engine()
    writer = GroupCommitWriter(engine, interval_ms=_interval_ms)

    send_log = SendLog(Source, Server, ManualClock(Write_Path_Start_Time), writer)

    for start in range(0, count, batch_size):
        greenlets:'anylist' = []

        for idx in range(start, start + batch_size):
            sent = new_sent_message(f'open-{idx:06d}')
            greenlet = spawn(send_log.record_first_attempt, sent)
            greenlets.append(greenlet)

        _ = joinall(greenlets, raise_error=True)

    writer.stop()

    print(json.dumps({'open': count}), flush=True)

# ################################################################################################################################

def fail_address(address:'str', ca_cert:'str', count:'int') -> 'None':
    """ Sends requests to an address that answers each with a transport failure, records each failure,
    and reports the state of the address before the process ends.
    """
    engine = get_audit_engine()
    writer = GroupCommitWriter(engine, interval_ms=_interval_ms)

    registry = AddressRegistry(writer, AuditSource.EbMS2, Server, SystemClock())
    _ = registry.load()

    context = ssl.create_default_context(cafile=ca_cert)

    for _ in range(count):
        request = Request(address, data=b'', method='POST')

        try:
            with urlopen(request, timeout=_request_timeout_seconds, context=context) as response:
                _ = response.read()
            registry.record_success(address)

        except HTTPError as e:
            if is_transport_error(e):
                _ = registry.record_failure(address)
            else:
                registry.record_success(address)

    writer.stop()

    record = registry.get(address)
    print(json.dumps({'state': record.state, 'consecutive_failures': record.consecutive_failures}), flush=True)

# ################################################################################################################################
# ################################################################################################################################

def main() -> 'None':

    mode = sys.argv[1]
    args = sys.argv[2:]

    if mode == 'write':
        write_events(int(args[0]), int(args[1]))

    elif mode == 'claim':
        claim_shared(float(args[0]), int(args[1]))

    elif mode == 'kill-before':
        kill_before_commit(args[0])

    elif mode == 'kill-after':
        kill_after_commit(args[0])

    elif mode == 'kill-before-confirm':
        kill_before_confirm(args[0])

    elif mode == 'seed-open':
        seed_open(int(args[0]), int(args[1]))

    elif mode == 'fail-address':
        fail_address(args[0], args[1], int(args[2]))

    else:
        raise Exception(f'Unknown mode `{mode}`')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
