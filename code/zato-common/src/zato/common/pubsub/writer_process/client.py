# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The worker's side of the stream to the pub/sub writer process. A caller sends its item and waits for the reply
# in its own greenlet, so a waiting publisher suspends one greenlet and never the hub. The arbiter holds the listening
# socket of the writer, so a connection is accepted by whichever writer runs, and the end of the stream tells
# the worker that the writer terminated. The worker then connects again and sends every item whose reply it did not
# receive, in the order in which the items were first sent, before any item sent after it.

# stdlib
import socket as stdlib_socket
from dataclasses import dataclass
from logging import getLogger
from time import monotonic

# gevent
import gevent
from gevent.event import AsyncResult
from gevent.lock import Semaphore
from gevent.socket import socket

# Zato
from zato.common.pubsub.writer_process.frames import FrameReader, new_item, WriterItemError
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.typing_ import any_, anydict, callable_, dict_

    any_ = any_
    anydict = anydict
    callable_ = callable_
    Greenlet = Greenlet

    itemdict = dict_[int, 'PendingItem']

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How many bytes one read of the stream takes at most
    Read_Size = 65536

# ################################################################################################################################
# ################################################################################################################################

class WriterTimeout(Exception):
    """ No reply to an item arrived within the deadline, which covers the restarts of the writer in the meantime.
    """

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PendingItem:
    """ An item sent to the writer whose reply did not arrive yet.
    """
    frame: 'bytes'
    result: 'AsyncResult'

# ################################################################################################################################
# ################################################################################################################################

class WriterClient:
    """ Sends the items of one worker to the pub/sub writer process and returns the reply of each to its caller.
    """

    def __init__(self, address:'str', deadline:'float', on_reconnect:'callable_') -> 'None':

        # A caller waits for the reply of its item for up to deadline seconds, and on_reconnect runs once the items
        # without a reply were sent to a writer that replaced a terminated one
        self.address = address
        self.deadline = deadline
        self.on_reconnect = on_reconnect

        self.sock = socket(stdlib_socket.AF_UNIX, stdlib_socket.SOCK_STREAM)
        self.is_connected = False
        self.is_closed = False

        self.next_item_id = 1
        self.pending:'itemdict' = {}

        # Guards the order in which frames enter the stream, so an item sent again precedes every later item
        self.lock = Semaphore()

# ################################################################################################################################

    def start(self) -> 'Greenlet':
        """ Starts the greenlet that connects to the writer and reads its replies, and returns it.
        """
        out = gevent.spawn(self._run)
        return out

# ################################################################################################################################

    def _run(self) -> 'None':

        is_first = True

        while not self.is_closed:

            # Each connection is accepted by the writer that runs at the time ..
            sock = socket(stdlib_socket.AF_UNIX, stdlib_socket.SOCK_STREAM)
            sock.connect(self.address)

            try:
                self._resend(sock)

                # .. a replacement of a terminated writer learns of the deliveries that it may owe ..
                if not is_first:
                    self.on_reconnect()

                is_first = False

                # .. and the replies are read until the writer terminates.
                self._read(sock)

            except OSError as e:
                logger.info('The connection to the pub/sub writer was closed -> %s', e)

            self.is_connected = False
            sock.close()

# ################################################################################################################################

    def _resend(self, sock:'socket') -> 'None':
        """ Sends every item without a reply over a new connection, in their original order.
        """
        with self.lock:
            self.sock.close()
            self.sock = sock

            for item in self.pending.values():
                sock.sendall(item.frame)

            self.is_connected = True

# ################################################################################################################################

    def _read(self, sock:'socket') -> 'None':
        reader = FrameReader()

        while data := sock.recv(ModuleCtx.Read_Size):
            for message in reader.feed(data):
                self._on_reply(message)

# ################################################################################################################################

    def _on_reply(self, message:'anydict') -> 'None':
        item_id = message['item_id']

        # The caller of an item whose deadline passed no longer waits for its reply
        if item_id in self.pending:
            item = self.pending.pop(item_id)
            item.result.set(message)

# ################################################################################################################################

    def call(self, kind:'str', body:'any_') -> 'any_':
        """ Sends one item to the writer and returns the body of its reply.
        """
        result = AsyncResult()

        # The writer runs the item only before the instant at which its caller stops waiting, so a copy of the item
        # that a writer reads after that instant is not run
        expires_at = monotonic() + self.deadline

        with self.lock:
            item_id = self.next_item_id
            self.next_item_id += 1

            item = PendingItem()
            item.frame = new_item(kind, item_id, expires_at, body)
            item.result = result

            self.pending[item_id] = item

            # Without a connection, the item is sent once the connection is made
            if self.is_connected:
                try:
                    self.sock.sendall(item.frame)
                except OSError as e:
                    logger.info('Could not send item %s to the pub/sub writer, sending it again on reconnect -> %s', item_id, e)
                    self.is_connected = False

        try:
            reply = result.get(timeout=self.deadline)
        except gevent.Timeout:
            _ = self.pending.pop(item_id)
            raise WriterTimeout(f'No reply from the pub/sub writer to item {item_id} within {self.deadline}s') from None

        message = cast_('anydict', reply)

        if 'error_type' in message:
            raise WriterItemError(message['error_type'], message['error'])

        out = message['body']
        return out

# ################################################################################################################################

    def close(self) -> 'None':
        self.is_closed = True
        self.sock.close()

# ################################################################################################################################
# ################################################################################################################################
