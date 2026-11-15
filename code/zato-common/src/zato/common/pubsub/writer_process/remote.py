# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The worker's side of the writes to the SQLite pub/sub file. A worker of a server with a writer process sends
# its publications, acknowledgements and leases to the writer, and a worker of a server without one, which is a server
# with one worker or with PostgreSQL, writes them itself, as a server of one process does. The audit log of a worker
# reaches the same writer through get_writer_client.

# stdlib
from types import SimpleNamespace

# Zato
from zato.common.db_env.engine import call_database
from zato.common.pubsub.sql.pull import lease_messages
from zato.common.pubsub.sql.writes import PubSubDuplicateMsgID, PubSubWriter
from zato.common.pubsub.writer_process.client import WriterClient
from zato.common.pubsub.writer_process.frames import ItemKind, WriterItemError

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Engine
    from zato.common.pubsub.sql.writes import PendingAck, PendingPublication
    from zato.common.typing_ import any_, anylist, callable_, intdict

    any_ = any_
    anylist = anylist
    callable_ = callable_
    Engine = Engine
    intdict = intdict
    PendingAck = PendingAck
    PendingPublication = PendingPublication

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The type of the error by which the writer reports a message identifier of a different message
    Duplicate_Msg_ID_Error = PubSubDuplicateMsgID.__name__

# ################################################################################################################################
# ################################################################################################################################

class _WriterConnection:
    """ The connection of this worker to the writer process, if the server runs one.
    """
    client:'WriterClient | None' = None

# ################################################################################################################################
# ################################################################################################################################

def start_writer_client(address:'str', deadline:'float', on_reconnect:'callable_') -> 'WriterClient':
    """ Connects this worker to the writer process, after which its publications, acknowledgements and leases
    go to the writer.
    """
    client = WriterClient(address, deadline, on_reconnect)
    _ = client.start()

    _WriterConnection.client = client

    out = client
    return out

# ################################################################################################################################

def get_writer_client() -> 'WriterClient | None':
    """ Returns the connection of this worker to the writer process, or None in a server that runs no writer process.
    """
    out = _WriterConnection.client
    return out

# ################################################################################################################################

def stop_writer_client() -> 'None':
    """ Closes the connection of this worker to the writer process.
    """
    client = _WriterConnection.client

    if client is not None:
        client.close()
        _WriterConnection.client = None

# ################################################################################################################################
# ################################################################################################################################

class RemotePubSubWriter:
    """ Writes publications and acknowledgements through the writer process, with the interface of PubSubWriter.
    """

    def __init__(self, client:'WriterClient') -> 'None':
        self.client = client

# ################################################################################################################################

    def _call(self, kind:'str', body:'any_') -> 'any_':
        """ Sends one item and returns the body of its reply, raising a duplicate identifier as the writer raised it.
        """
        try:
            out = self.client.call(kind, body)
        except WriterItemError as e:
            if e.error_type == ModuleCtx.Duplicate_Msg_ID_Error:
                raise PubSubDuplicateMsgID(e.error) from None
            raise

        return out

# ################################################################################################################################

    def publish(self, pending:'PendingPublication') -> 'None':
        body = {'message_values': pending.message_values}
        reply = self._call(ItemKind.Publish, body)

        pending.subscriber_keys = reply['subscriber_keys']

# ################################################################################################################################

    def ack(self, pending:'PendingAck') -> 'None':
        body = {
            'sub_key': pending.sub_key,
            'msg_ids': pending.msg_ids,
            'sequence_ids': pending.sequence_ids,
        }
        reply = self._call(ItemKind.Ack, body)

        pending.removed_count = reply['removed_count']
        pending.fully_delivered_count = reply['fully_delivered_count']

# ################################################################################################################################
# ################################################################################################################################

def new_pubsub_writer() -> 'PubSubWriter | RemotePubSubWriter':
    """ Returns the writer of the publications and acknowledgements of this worker.
    """
    client = _WriterConnection.client

    if client is None:
        out = PubSubWriter()
    else:
        out = RemotePubSubWriter(client)

    return out

# ################################################################################################################################

def lease(
    engine:'Engine',
    sub_key:'str',
    max_messages:'int',
    max_len:'int',
    now_ms:'int',
    leased_until_ms:'int',
) -> 'tuple[anylist, intdict]':
    """ Leases the deliverable rows of one subscriber, through the writer process if the server runs one,
    and returns the rows of their messages with the attempt number of each, by message ID.
    """
    client = _WriterConnection.client

    # Without a writer process, the worker leases the rows itself ..
    if client is None:
        out = call_database(engine, lease_messages, engine, sub_key, max_messages, max_len, now_ms, leased_until_ms)
        return out

    # .. otherwise the writer leases them ..
    body = {
        'sub_key': sub_key,
        'max_messages': max_messages,
        'max_len': max_len,
        'now_ms': now_ms,
        'leased_until_ms': leased_until_ms,
    }
    reply = client.call(ItemKind.Lease, body)

    # .. and the rows are read by their attributes, as the rows of the database are.
    rows:'anylist' = []

    for row_values in reply['rows']:
        row = SimpleNamespace(**row_values)
        rows.append(row)

    attempts:'intdict' = {}

    for message_id, attempt in reply['attempts']:
        attempts[message_id] = attempt

    out = (rows, attempts)
    return out

# ################################################################################################################################
# ################################################################################################################################
