# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The client of the replication barrier of the active-standby node. A request is the name of a database followed
# by a newline. The node answers `ok` once every frame of that database committed before the request is stored
# on the standby, or synced locally while the node runs alone, `replaced` when the node is no longer active,
# and `error` followed by a description when the request cannot be answered.

# stdlib
import socket

# Zato
from zato.common.ha.common import get_barrier_socket_path
from zato.common.pubsub.sql.replaced import PubSubReplaced

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long a request waits for the answer of the node, in seconds. A barrier waits at most for the time
    # after which the node removes an unresponsive standby, followed by one write to the referee.
    Timeout_Seconds = 30.0

    # The answers of the node
    Answer_OK       = 'ok'
    Answer_Replaced = 'replaced'

    # The longest answer that is read, in bytes
    Max_Answer_Size = 4096

    # The character that ends a request and an answer
    Line_End = b'\n'

# ################################################################################################################################
# ################################################################################################################################

class BarrierError(Exception):
    """ Raised when the node cannot be reached or cannot answer a barrier request.
    """

# ################################################################################################################################
# ################################################################################################################################

def _read_answer(connection:'socket.socket') -> 'str':
    """ Reads one answer of the node, up to the end of its line.
    """
    received = b''

    while not received.endswith(ModuleCtx.Line_End):
        chunk = connection.recv(ModuleCtx.Max_Answer_Size)

        # The node closed the connection before it answered ..
        if not chunk:
            raise BarrierError('The active-standby node closed the barrier connection without an answer')

        received += chunk

        # .. or it sent more than any answer it can produce.
        if len(received) > ModuleCtx.Max_Answer_Size:
            raise BarrierError('The answer of the active-standby node exceeds the maximum size')

    answer = received.decode('utf8')

    out = answer.strip()
    return out

# ################################################################################################################################

def wait_for_replication(database:'str') -> 'None':
    """ Returns once every commit of a database made before the call is stored on the standby or synced locally.
    For a database shipped asynchronously, returns at once if the node serves requests. Raises PubSubReplaced
    if the node is no longer active and BarrierError if the node cannot answer.
    """
    path = get_barrier_socket_path()
    request = database.encode('utf8') + ModuleCtx.Line_End

    # Send the name of the database ..
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(ModuleCtx.Timeout_Seconds)
            connection.connect(path)
            connection.sendall(request)

            # .. and wait for the node to answer.
            answer = _read_answer(connection)

    except OSError as e:
        raise BarrierError(f'Replication barrier of `{database}` not answered through `{path}` -> {e}') from e

    # The commits are stored ..
    if answer == ModuleCtx.Answer_OK:
        return

    # .. this node no longer serves requests ..
    elif answer == ModuleCtx.Answer_Replaced:
        raise PubSubReplaced(f'The active-standby node of this server is no longer active, database `{database}`')

    # .. and anything else is an error that the node describes.
    else:
        raise BarrierError(f'Replication barrier of `{database}` failed -> {answer}')

# ################################################################################################################################
# ################################################################################################################################
