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
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

# SQLAlchemy
from sqlalchemy import event as sa_event

# Zato
from live_db import Line_Claimed, Line_Committing, Line_Ready, new_audit_log, new_event
from zato.common.audit_log.api import get_audit_engine
from zato.common.b2b.common.commit_group import GroupCommitWriter
from zato.common.b2b.common.commit_sql import ClaimWrite
from zato.common.b2b.common.store import MessageStore
from zato.common.test.b2b_write_path import new_identity, new_stored_message

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

# ################################################################################################################################
# ################################################################################################################################

def _report(data:'any_') -> 'None':
    print(json.dumps(data), flush=True)

# ################################################################################################################################

def _say(line:'str') -> 'None':
    print(line, flush=True)

# ################################################################################################################################

def write_events(batches:'int', batch_size:'int') -> 'None':
    """ Commits batches of events, each with its attribute and body, while the parent commits its own.
    """
    engine = get_audit_engine()
    writer = GroupCommitWriter(engine, interval_ms=0, max_rows=_max_rows, is_started=False)
    audit_log = new_audit_log()

    _say(Line_Ready)

    count = 0

    for batch_idx in range(batches):
        for idx in range(batch_size):
            _ = writer.enqueue(new_event(audit_log, f'child-{batch_idx}-{idx}'), 3)
            count += 1

        _ = writer.commit_due()

    _report({'events': count})

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

    _report({'claimed': claimed})

# ################################################################################################################################

def kill_before_commit(message_id:'str') -> 'None':
    """ Claims a message and waits to be stopped while the commit of the claim has not completed.
    """
    engine = get_audit_engine()
    writer = GroupCommitWriter(engine, interval_ms=_interval_ms)
    store = MessageStore(writer)

    def on_commit(conn:'any_') -> 'None':
        _say(Line_Committing)
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

    _say(Line_Claimed)
    time.sleep(_wait_for_kill_seconds)

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

    else:
        raise Exception(f'Unknown mode `{mode}`')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
# ################################################################################################################################
