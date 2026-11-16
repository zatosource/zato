# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The arbiter's side of the control channel. The hub holds one SEQPACKET socket for the worker and one for the config
# process, relays the events of each to the other in the order of their sequence numbers, holds the events of a starting
# process until it reports ready, sends the queries of the config process to the worker and returns their results,
# and sends drain, reload and log reopen commands. Its sockets are non-blocking, and a datagram that a socket cannot
# take waits in the queue of its slot, so a process that reads nothing never holds the arbiter.

# stdlib
import os
import socket
from collections import deque
from dataclasses import dataclass
from logging import getLogger
from select import POLLIN, POLLOUT
from time import monotonic

# Zato
from zato.common.worker_slot import ModuleCtx as WorkerSlotCtx
from zato.server.control.config_route import ConfigRoute
from zato.server.control.envelope import decode, encode, join, MessageType, ModuleCtx as EnvelopeCtx, new_body_path, \
    new_message, split

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, callable_, dict_, floatnone, list_, set_, tuple_

    any_ = any_
    anydict = anydict
    callable_ = callable_
    floatnone = floatnone

    bytesdeque     = deque[bytes]
    intset         = set_[int]
    pollevents     = list_[tuple_[int, int]]
    channellist    = list_['SlotChannel']
    intchanneldict = dict_[int, 'SlotChannel']
    querydict      = dict_[str, 'PendingQuery']

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # How long a query waits for the response of the worker, in seconds
    Query_Timeout = 5.0

# ################################################################################################################################
# ################################################################################################################################

class EntryStatus:

    # The worker responded within the deadline
    OK = 'ok'

    # The worker did not respond within the deadline
    Timeout = 'timeout'

    # No worker that reported ready ran when the query was received, or the worker terminated
    Unavailable = 'unavailable'

# ################################################################################################################################
# ################################################################################################################################

def new_entry(status:'str', body:'any_') -> 'anydict':
    """ Returns the result of a query.
    """
    out = {
        'status': status,
        'body': body,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class SlotChannel:
    """ The arbiter's end of the control socket of the worker or of the config process.
    """
    slot: 'int'
    sock: 'socket.socket'

    # Whether the process reported ready, before which relayed messages wait in the startup buffer
    is_ready: 'bool'

    # Whether the process closed its end and every datagram it sent was read, after which the socket is no longer polled
    is_eof: 'bool'

    # Whether the socket refused a datagram because the process closed its end, after which nothing is sent to it
    is_broken: 'bool'

    # The datagrams that the socket has not taken yet
    out_queue: 'bytesdeque'

    # The datagrams that wait for the process to report ready
    startup_buffer: 'bytesdeque'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class PendingQuery:
    """ A query that the arbiter sent to the worker and whose response it waits for.
    """
    cid: 'str'
    origin_slot: 'int'
    deadline: 'float'

# ################################################################################################################################
# ################################################################################################################################

class ControlHub:
    """ Relays the messages of the control channel between the worker and the config process of one arbiter.
    """

    def __init__(
        self,
        body_dir:'str',
        query_timeout:'float',
        on_ready:'callable_',
        on_logs_reopened:'callable_',
        on_replaced:'callable_',
        ) -> 'None':

        # The hub calls on_ready with a slot whose process reported ready, on_logs_reopened with a slot
        # whose process reopened its log files and with the ID of the rotation that it acknowledges,
        # and on_replaced with a slot whose process learned that another server took over the pub/sub database
        self.body_dir         = body_dir
        self.query_timeout    = query_timeout
        self.on_ready         = on_ready
        self.on_logs_reopened = on_logs_reopened
        self.on_replaced      = on_replaced

        self.seq = EnvelopeCtx.No_Sequence
        self.channels:'intchanneldict' = {}
        self.fd_to_channel:'intchanneldict' = {}
        self.queries:'querydict' = {}

        # The messages between the worker and the config process follow routes of their own
        self.config_route = ConfigRoute(self)

# ################################################################################################################################

    def open_slot(self, slot:'int') -> 'socket.socket':
        """ Creates the control socket of a slot before its process is forked and returns the end of the process.
        """
        arbiter_end, worker_end = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        arbiter_end.setblocking(False)

        channel = SlotChannel()
        channel.slot = slot
        channel.sock = arbiter_end
        channel.is_ready = False
        channel.is_eof = False
        channel.is_broken = False
        channel.out_queue = deque()
        channel.startup_buffer = deque()

        self.channels[slot] = channel
        self.fd_to_channel[arbiter_end.fileno()] = channel

        # A new config process continues from the loads that its predecessor left
        if slot == WorkerSlotCtx.Config_Slot:
            self.config_route.on_config_opened(channel)

        out = worker_end
        return out

# ################################################################################################################################

    def close_in_worker(self) -> 'None':
        """ Closes in a forked process the ends of the arbiter, which the process inherited.
        """
        for channel in self.channels.values():
            channel.sock.close()

# ################################################################################################################################

    def remove_body_file(self, datagram:'bytes') -> 'None':
        header, _ = split(datagram)

        if path := header.get('path'):
            os.remove(path)

# ################################################################################################################################

    def close_slot(self, slot:'int') -> 'None':
        """ Closes the control socket of a slot whose process terminated, together with the datagrams it did not receive.
        """
        # The process may have sent datagrams after the last poll, which are read up to the end of the stream
        self._receive(self.channels[slot])

        channel = self.channels.pop(slot)
        _ = self.fd_to_channel.pop(channel.sock.fileno())
        channel.sock.close()

        # The bodies of the datagrams that the process never received have no other reader ..
        for datagram in channel.out_queue:
            self.remove_body_file(datagram)

        for datagram in channel.startup_buffer:
            self.remove_body_file(datagram)

        # .. the queries that wait for it are answered without it ..
        if slot == WorkerSlotCtx.Worker_Slot:
            for query in list(self.queries.values()):
                self._complete(query, EntryStatus.Unavailable, None)

        # .. and the forwarded invocations and the loads that involve it are resolved.
        self.config_route.on_slot_closed(slot)

# ################################################################################################################################

    def close_all(self) -> 'None':
        for slot in list(self.channels):
            self.close_slot(slot)

# ################################################################################################################################

    def get_poll_requests(self) -> 'pollevents':
        """ Returns each descriptor that the arbiter polls and the events it polls for.
        """
        out:'pollevents' = []

        for channel in self.channels.values():
            if channel.is_eof:
                continue

            events = POLLIN

            if channel.out_queue:
                if not channel.is_broken:
                    events |= POLLOUT

            fd = channel.sock.fileno()
            out.append((fd, events))

        return out

# ################################################################################################################################

    def handle_poll_events(self, poll_events:'pollevents') -> 'None':
        """ Receives and sends the datagrams of the descriptors that the poll of the arbiter reported.
        """
        for fd, events in poll_events:
            channel = self.fd_to_channel.get(fd)

            # The descriptor belongs to the arbiter itself, or to a slot that closed within this poll
            if not channel:
                continue

            if events & POLLOUT:
                self._flush(channel)

            # A hang-up is reported with data still to read, and the read reports the end of the stream
            if events & ~POLLOUT:
                self._receive(channel)

# ################################################################################################################################

    def _flush(self, channel:'SlotChannel') -> 'None':
        """ Sends to the process of a slot as many queued datagrams as its socket takes.
        """
        while channel.out_queue:
            if channel.is_broken:
                return

            datagram = channel.out_queue[0]

            try:
                _ = channel.sock.send(datagram)
            except BlockingIOError:
                return

            # The process terminated, and its datagrams are removed when the arbiter reaps it
            except (BrokenPipeError, ConnectionResetError):
                channel.is_broken = True
                return

            _ = channel.out_queue.popleft()

# ################################################################################################################################

    def send(self, channel:'SlotChannel', datagram:'bytes') -> 'None':
        channel.out_queue.append(datagram)
        self._flush(channel)

# ################################################################################################################################

    def discard_startup_buffer(self, channel:'SlotChannel') -> 'None':
        """ Discards the datagrams held for a starting process, whose load of its configuration contains them.
        """
        while channel.startup_buffer:
            datagram = channel.startup_buffer.popleft()
            self.remove_body_file(datagram)

# ################################################################################################################################

    def deliver(self, channel:'SlotChannel', datagram:'bytes') -> 'None':
        """ Sends a relayed datagram to a ready process, or holds it until the process reports ready.
        """
        if channel.is_ready:
            self.send(channel, datagram)
        else:
            channel.startup_buffer.append(datagram)

# ################################################################################################################################

    def _next_seq(self) -> 'int':
        self.seq += 1
        out = self.seq
        return out

# ################################################################################################################################

    def _receive(self, channel:'SlotChannel') -> 'None':
        """ Handles every datagram that the process of a slot sent.
        """
        while True:
            try:
                datagram = channel.sock.recv(EnvelopeCtx.Max_Datagram)
            except BlockingIOError:
                return
            except ConnectionResetError:
                datagram = b''

            # The process closed its end, and the arbiter closes the slot when it reaps the process
            if not datagram:
                channel.is_eof = True
                return

            self._handle(channel, datagram)

# ################################################################################################################################

    def _handle(self, channel:'SlotChannel', datagram:'bytes') -> 'None':
        header, body = split(datagram)
        message_type = header['type']

        if message_type == MessageType.Event:
            self._relay(channel.slot, header, body, MessageType.Event)

        elif message_type == MessageType.Ready:
            self._on_ready(channel)

        elif message_type == MessageType.Query:
            self._send_query(channel.slot, header, body)

        elif message_type == MessageType.Response:
            self._on_response(datagram)

        elif message_type == MessageType.Logs_Reopened:
            message = decode(datagram)
            self.on_logs_reopened(channel.slot, message.body)

        elif message_type == MessageType.Replaced:
            self.on_replaced(channel.slot)

        elif message_type == MessageType.Forward:
            self.config_route.on_forward(channel, header, body)

        elif message_type == MessageType.Forward_Result:
            self.config_route.on_forward_result(header, datagram)

        elif message_type == MessageType.Load_Request:
            self.config_route.on_load_request(channel, header, body)

        elif message_type == MessageType.Mark:
            self.config_route.on_mark(header, datagram)

        elif message_type == MessageType.Load_Done:
            self.config_route.on_load_done(channel, header, body)

        # The config process asks for a reload of the worker after a change that reached the ODB without its events
        elif message_type == MessageType.Reload:
            self.broadcast_reload()

        else:
            logger.warning('Ignoring control message of type `%s` from slot %s', message_type, channel.slot)

# ################################################################################################################################

    def _on_ready(self, channel:'SlotChannel') -> 'None':
        """ Delivers to a process that reported ready the datagrams that were relayed during its startup.
        """
        channel.is_ready = True

        while channel.startup_buffer:
            datagram = channel.startup_buffer.popleft()
            self.send(channel, datagram)

        self.on_ready(channel.slot)

# ################################################################################################################################

    def _get_recipients(self, origin_slot:'int') -> 'channellist':
        out:'channellist' = []

        for channel in self.channels.values():
            if channel.slot != origin_slot:
                out.append(channel)

        return out

# ################################################################################################################################

    def _relay(self, origin_slot:'int', header:'anydict', body:'bytes', message_type:'str') -> 'None':
        """ Sends a message with the next sequence number to every slot other than its origin.
        """
        header['type'] = message_type
        header['seq'] = self._next_seq()
        header['slot'] = origin_slot

        source_path = header.get('path')

        for channel in self._get_recipients(origin_slot):

            # Each recipient removes the body file it reads, so each receives a link of its own ..
            if source_path:
                link_path = new_body_path(self.body_dir)
                os.link(source_path, link_path)
                header['path'] = link_path

            datagram = join(header, body)
            self.deliver(channel, datagram)

        # .. and the file that the origin wrote has no reader.
        if source_path:
            os.remove(source_path)

# ################################################################################################################################

    def broadcast_reload(self) -> 'None':
        """ Requests the worker to read its configuration again, which a starting worker does after it reports ready.
        The config process commits every change itself, so it receives no such request.
        """
        message = new_message(MessageType.Reload, None)
        datagram = encode(message, self.body_dir)
        header, body = split(datagram)

        self._relay(WorkerSlotCtx.Config_Slot, header, body, MessageType.Reload)

# ################################################################################################################################

    def send_drain(self, slot:'int') -> 'None':
        """ Sends the drain command to the process of a slot, whether or not it reported ready.
        """
        message = new_message(MessageType.Drain, None)
        message.seq = self._next_seq()

        datagram = encode(message, self.body_dir)
        channel = self.channels[slot]

        self.send(channel, datagram)

# ################################################################################################################################

    def broadcast_reopen_logs(self, rotation_id:'int') -> 'intset':
        """ Asks the process of every open slot to reopen its log files, a starting one included, and returns those slots.
        The command does not wait in the startup buffer, because a starting process writes to the renamed files already.
        """
        out:'intset' = set()

        for channel in self.channels.values():
            message = new_message(MessageType.Reopen_Logs, rotation_id)
            message.seq = self._next_seq()

            datagram = encode(message, self.body_dir)
            self.send(channel, datagram)

            out.add(channel.slot)

        return out

# ################################################################################################################################

    def _send_query(self, origin_slot:'int', header:'anydict', body:'bytes') -> 'None':
        """ Sends a query to the worker, or completes it as unavailable if no worker that reported ready runs.
        """
        query = PendingQuery()
        query.cid = header['cid']
        query.origin_slot = origin_slot
        query.deadline = monotonic() + self.query_timeout

        self.queries[query.cid] = query

        header['seq'] = self._next_seq()
        header['slot'] = origin_slot

        channel = self.channels.get(WorkerSlotCtx.Worker_Slot)

        if channel and channel.is_ready:
            datagram = join(header, body)
            self.send(channel, datagram)
        else:
            if source_path := header.get('path'):
                os.remove(source_path)

            self._complete(query, EntryStatus.Unavailable, None)

# ################################################################################################################################

    def _on_response(self, datagram:'bytes') -> 'None':
        message = decode(datagram)

        # A response that arrives after the deadline of its query belongs to a result returned already
        if query := self.queries.get(message.cid):
            self._complete(query, EntryStatus.OK, message.body)

# ################################################################################################################################

    def _complete(self, query:'PendingQuery', status:'str', body:'any_') -> 'None':
        """ Returns the result of a query to its origin.
        """
        _ = self.queries.pop(query.cid)
        entry = new_entry(status, body)

        # The origin may have terminated while the query waited
        if channel := self.channels.get(query.origin_slot):
            message = new_message(MessageType.Query_Result, entry, query.cid)
            message.seq = self._next_seq()

            datagram = encode(message, self.body_dir)
            self.send(channel, datagram)

# ################################################################################################################################

    def get_next_deadline(self) -> 'floatnone':
        """ Returns the earliest deadline of the pending queries, if there are any.
        """
        out = None

        for query in self.queries.values():
            if out is None:
                out = query.deadline
            else:
                out = min(out, query.deadline)

        return out

# ################################################################################################################################

    def expire_queries(self, now:'float') -> 'None':
        """ Completes as timed out each query to which the worker did not respond before its deadline.
        """
        for query in list(self.queries.values()):
            if query.deadline <= now:
                self._complete(query, EntryStatus.Timeout, None)

# ################################################################################################################################
# ################################################################################################################################
