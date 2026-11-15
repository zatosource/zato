# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import timedelta
from multiprocessing import get_context

# gevent
import gevent

# SQLAlchemy
from sqlalchemy import select

# Zato
from zato.common.pubsub.sql.clock import get_database_clock
from zato.common.pubsub.sql.config import get_pubsub_engine
from zato.common.pubsub.sql.schema import message_table
from zato.common.util.time_ import datetime_to_ms

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anytuple, callable_, intlist

    anydict = anydict
    anytuple = anytuple
    callable_ = callable_
    intlist = intlist

# ################################################################################################################################
# ################################################################################################################################

# The topic of the publications, which has no subscribers, so that each message is a trace from its insert on
Topic_Name = 'writer.test.topic'

# How long a message of the tests is valid, in seconds
_expiration = 86_400

# How long a test waits for the process that runs its body, in seconds
_join_timeout = 60.0

# The body of a test runs in a forked process, as the workers of a server run
_context = get_context('fork')

# ################################################################################################################################
# ################################################################################################################################

def new_message_values(msg_id:'str', age_seconds:'int'=0) -> 'anydict':
    """ Returns the values of a message row as SQLPubSubBackend.publish builds them, received age_seconds ago.
    """
    age = timedelta(seconds=age_seconds)
    received = get_database_clock().now() - age
    received_iso = received.isoformat()
    received_ms = int(datetime_to_ms(received))

    expires = received + timedelta(seconds=_expiration)
    expires_iso = expires.isoformat()
    expires_ms = int(datetime_to_ms(expires))

    out = {
        'msg_id': msg_id,
        'topic_name': Topic_Name,
        'payload': 'payload',
        'payload_encrypted': False,
        'payload_crc32': 1,
        'data_class': None,
        'data_size': 7,
        'data_preview': None,
        'priority': 5,
        'expiration': _expiration,
        'pub_time_iso': received_iso,
        'recv_time_iso': received_iso,
        'expiration_time_iso': expires_iso,
        'pub_time_ms': received_ms,
        'expiration_ms': expires_ms,
        'publisher': None,
        'cid': None,
        'correl_id': None,
        'in_reply_to': None,
        'ext_client_id': None,
    }
    return out

# ################################################################################################################################

def get_message_ids(msg_id:'str') -> 'intlist':
    """ Returns the primary keys of the message rows with the given msg_id.
    """
    query = select(message_table.c.id)
    query = query.where(message_table.c.msg_id == msg_id)

    out:'intlist' = []

    with get_pubsub_engine().connect() as connection:
        for row in connection.execute(query):
            out.append(row.id)

    return out

# ################################################################################################################################

def _run_reinitialized(target:'callable_', args:'anytuple') -> 'None':
    """ Gives the forked process an event loop of its own before the test body runs, as the arbiter does for its workers.
    """
    gevent.reinit()
    target(*args)

# ################################################################################################################################

def run_in_child(target:'callable_', args:'anytuple') -> 'None':
    """ Runs one test body in a forked process, so that the engines and the checkpoint threads it starts
    remain in that process and no process that a later test forks inherits them.
    """
    process = _context.Process(target=_run_reinitialized, args=(target, args))
    process.start()
    process.join(_join_timeout)

    assert process.exitcode == 0

# ################################################################################################################################
# ################################################################################################################################
