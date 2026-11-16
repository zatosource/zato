# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The side of the control channel of the worker and of the config process. One greenlet reads the datagrams of the arbiter and applies the events
# in the order in which they arrive, which is the order of their sequence numbers. Each query runs in a greenlet
# of its own, so a slow query never holds the events that follow it.

# stdlib
import socket as stdlib_socket
from logging import getLogger

# gevent
import gevent
from gevent.event import AsyncResult
from gevent.socket import socket

# Zato
from zato.common.typing_ import cast_
from zato.server.control.envelope import decode, encode, MessageType, ModuleCtx as EnvelopeCtx, new_cid, new_message

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from gevent import Greenlet
    from zato.common.typing_ import any_, anydict, callable_, dict_
    from zato.server.control.envelope import Message

    any_ = any_
    anydict = anydict
    callable_ = callable_
    Greenlet = Greenlet
    Message = Message

    resultdict  = dict_[str, AsyncResult]

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The messages that complete a call of this process that waits for them
_call_results = {MessageType.Query_Result, MessageType.Forward_Result, MessageType.Mark}

# ################################################################################################################################
# ################################################################################################################################

class ControlClient:
    """ Sends the messages of one process to the arbiter and applies the messages that the arbiter sends to it.
    """

    def __init__(
        self,
        control_fd:'int',
        body_dir:'str',
        on_event:'callable_',
        on_query:'callable_',
        on_drain:'callable_',
        on_reload:'callable_',
        on_reopen_logs:'callable_',
        ) -> 'None':

        # on_event receives each relayed event as a message, and on_query the body of each query, returning its response
        self.sock = socket(stdlib_socket.AF_UNIX, stdlib_socket.SOCK_SEQPACKET, 0, control_fd)
        self.body_dir       = body_dir
        self.on_event       = on_event
        self.on_query       = on_query
        self.on_drain       = on_drain
        self.on_reload      = on_reload
        self.on_reopen_logs = on_reopen_logs

        self.results:'resultdict' = {}

        # The handlers of the messages that only some processes receive, by the type of a message,
        # each called with the message in the greenlet that reads the channel
        self.handlers:'dict[str, callable_]' = {}

# ################################################################################################################################

    def start(self) -> 'Greenlet':
        """ Starts the greenlet that reads the messages of the arbiter and returns it.
        """
        out = gevent.spawn(self._read)
        return out

# ################################################################################################################################

    def send(self, message:'Message') -> 'None':
        datagram = encode(message, self.body_dir)
        _ = self.sock.send(datagram)

# ################################################################################################################################

    def report_ready(self) -> 'None':
        """ Tells the arbiter that the process loaded its configuration, after which the arbiter relays events to it.
        """
        message = new_message(MessageType.Ready, None)
        self.send(message)

# ################################################################################################################################

    def report_replaced(self) -> 'None':
        """ Tells the arbiter that another server took over the pub/sub database, after which the arbiter drains its processes.
        """
        message = new_message(MessageType.Replaced, None)
        self.send(message)

# ################################################################################################################################

    def publish(self, body:'any_') -> 'None':
        """ Sends an event that the arbiter relays to the other process.
        """
        message = new_message(MessageType.Event, body)
        self.send(message)

# ################################################################################################################################

    def query(self, body:'any_') -> 'anydict':
        """ Sends a query to the worker and returns its result, with the status and the body of the response,
        which the arbiter returns within the deadline of the query.
        """
        cid = new_cid()

        result = AsyncResult()
        self.results[cid] = result

        message = new_message(MessageType.Query, body, cid)
        self.send(message)

        out = result.get()
        out = cast_('anydict', out)
        return out

# ################################################################################################################################

    def forward(self, body:'any_') -> 'any_':
        """ Sends an invocation of a service that changes configuration to the config process and returns its result,
        which the arbiter delivers after the events of the change, so the worker has applied them when this returns.
        """
        cid = new_cid()

        result = AsyncResult()
        self.results[cid] = result

        message = new_message(MessageType.Forward, body, cid)
        self.send(message)

        out = result.get()
        return out

# ################################################################################################################################

    def request_load(self) -> 'str':
        """ Asks the config process for a load of the configuration and returns the correlation ID of the request
        once its mark arrived, after which no change is in progress until the worker reports the load done.
        """
        cid = new_cid()

        result = AsyncResult()
        self.results[cid] = result

        message = new_message(MessageType.Load_Request, None, cid)
        self.send(message)

        _ = result.get()

        out = cid
        return out

# ################################################################################################################################

    def report_load_done(self, cid:'str') -> 'None':
        """ Tells the config process that the worker loaded its configuration after the mark of a request.
        """
        message = new_message(MessageType.Load_Done, None, cid)
        self.send(message)

# ################################################################################################################################

    def _respond(self, query:'Message') -> 'None':
        body = self.on_query(query.body)

        message = new_message(MessageType.Response, body, query.cid)
        self.send(message)

# ################################################################################################################################

    def _reopen_logs(self, command:'Message') -> 'None':
        """ Reopens the log files that the arbiter renamed and acknowledges the rotation, whose ID is the body of the command.
        """
        self.on_reopen_logs()

        message = new_message(MessageType.Logs_Reopened, command.body)
        self.send(message)

# ################################################################################################################################

    def _read(self) -> 'None':
        """ Applies the messages of the arbiter until the arbiter closes its end.
        """
        while datagram := self.sock.recv(EnvelopeCtx.Max_Datagram):
            message = decode(datagram)

            if message.type == MessageType.Event:
                self.on_event(message)

            elif message.type == MessageType.Query:
                _ = gevent.spawn(self._respond, message)

            # The result of a query, of a forwarded invocation and the mark of a load each complete a call in progress
            elif message.type in _call_results:
                result = self.results.pop(message.cid)
                result.set(message.body)

            elif message.type == MessageType.Drain:
                self.on_drain()

            elif message.type == MessageType.Reload:
                self.on_reload()

            elif message.type == MessageType.Reopen_Logs:
                self._reopen_logs(message)

            elif message.type in self.handlers:
                handler = self.handlers[message.type]
                handler(message)

            else:
                logger.warning('Ignoring control message of type `%s`', message.type)

        logger.info('The arbiter closed the control channel')

# ################################################################################################################################

    def close(self) -> 'None':
        self.sock.close()

# ################################################################################################################################
# ################################################################################################################################
