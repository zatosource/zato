# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The writer's side of the streams of the workers. The writer accepts one connection per worker on the listening socket
# that the arbiter created, and runs each item it reads in a greenlet of its own, in the order of arrival,
# so the commit queue of the writer gathers the items of every worker into shared transactions.

# stdlib
import socket as stdlib_socket
from logging import getLogger
from time import monotonic

# gevent
import gevent
from gevent.lock import Semaphore
from gevent.socket import socket

# Zato
from zato.common.pubsub.writer_process.frames import FrameReader, new_error_reply, new_reply, WriterItemExpired

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, strcalldict

    anydict = anydict
    strcalldict = strcalldict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many bytes one read of a stream takes at most
    Read_Size = 65536

    # How many connections wait for the writer while it restarts, at least one per worker
    Listen_Backlog = 1024

# ################################################################################################################################
# ################################################################################################################################

def new_listening_socket(address:'str') -> 'stdlib_socket.socket':
    """ Creates the listening socket of the writer, which the arbiter holds across the restarts of the writer.
    """
    out = stdlib_socket.socket(stdlib_socket.AF_UNIX, stdlib_socket.SOCK_STREAM)
    out.bind(address)
    out.listen(ModuleCtx.Listen_Backlog)

    return out

# ################################################################################################################################
# ################################################################################################################################

class WriterServer:
    """ Accepts the connections of the workers and replies to each item with what its handler returns.
    """

    def __init__(self, listen_fd:'int', handlers:'strcalldict') -> 'None':

        # Each handler receives the body of an item of its kind and returns the body of the reply
        self.listen_sock = socket(stdlib_socket.AF_UNIX, stdlib_socket.SOCK_STREAM, 0, listen_fd)
        self.handlers = handlers

# ################################################################################################################################

    def serve_forever(self) -> 'None':
        while True:
            conn, _ = self.listen_sock.accept()
            _ = gevent.spawn(self._serve, conn)

# ################################################################################################################################

    def _serve(self, conn:'socket') -> 'None':
        """ Runs the items of one worker until the worker closes its end.
        """
        reader = FrameReader()

        # Guards the order of the replies within the stream, which the greenlets of the items write to
        lock = Semaphore()

        try:
            while data := conn.recv(ModuleCtx.Read_Size):
                for message in reader.feed(data):
                    _ = gevent.spawn(self._handle, conn, lock, message)

        except OSError as e:
            logger.info('The connection of a worker was closed -> %s', e)

        conn.close()

# ################################################################################################################################

    def _handle(self, conn:'socket', lock:'Semaphore', message:'anydict') -> 'None':
        item_id = message['item_id']
        handler = self.handlers[message['kind']]

        # CLOCK_MONOTONIC is common to all the processes of the host, so the caller of an item that expired
        # has stopped waiting for it and the item is not run ..
        if monotonic() >= message['expires_at']:
            reply = new_error_reply(item_id, WriterItemExpired(f'Item {item_id} expired before the writer ran it'))

        # .. and the error of one item reaches its caller as the error of a publication in one process does.
        else:
            try:
                body = handler(message['body'])
            except Exception as e:
                reply = new_error_reply(item_id, e)
            else:
                reply = new_reply(item_id, body)

        with lock:
            try:
                conn.sendall(reply)

            # A worker that terminated sends nothing again, and one that reconnected sends the item again
            except OSError as e:
                logger.info('Could not reply to item %s of a worker -> %s', item_id, e)

# ################################################################################################################################

    def close(self) -> 'None':
        self.listen_sock.close()

# ################################################################################################################################
# ################################################################################################################################
